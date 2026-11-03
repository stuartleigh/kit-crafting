"""Integration checks for independent releases, archive contents and download links."""
import hashlib
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import parse_qs, urlsplit
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from packs import MODS, ROOT, bump, package, validate
from build_site import build_site


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.downloads = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and "download" in attrs:
            self.downloads.append(attrs)


class PackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        for mod in MODS:
            for kind in ("bp", "rp"):
                shutil.copytree(mod.pack_dir(ROOT, kind), mod.pack_dir(cls.root, kind))
        shutil.copytree(ROOT / "site", cls.root / "site")
        package(cls.root)
        build_site(cls.root)

    def preserve_manifests(self):
        for mod in MODS:
            for kind in ("bp", "rp"):
                path = mod.pack_dir(self.root, kind) / "manifest.json"
                self.addCleanup(path.write_bytes, path.read_bytes())

    def packed(self, mod, kind):
        addon = self.root / "dist" / f"{mod.package}-{mod.version(self.root)}.mcaddon"
        with ZipFile(addon) as outer:
            self.assertIsNone(outer.testzip())
            self.assertEqual(len(outer.namelist()), 2)
            data = outer.read(f"{mod.package}-{kind.upper()}-{mod.version(self.root)}.mcpack")
        return ZipFile(BytesIO(data))

    def test_downloads_match_versions_and_checksums(self):
        site = self.root / "_site"
        catalog = json.loads((site / "mods.json").read_text())
        html = (site / "index.html").read_text()
        self.assertNotIn("{{", html)
        links = Links(html).downloads
        self.assertEqual(set(catalog), {"kit-crafting", "horror-kids"})
        self.assertEqual(len(links), 2)
        self.assertEqual(len(links), len(MODS))
        for mod, link in zip(MODS, links):
            metadata_path = "version.json" if mod.id == "kit-crafting" else f"{mod.id}-version.json"
            metadata = json.loads((site / metadata_path).read_text())
            target = urlsplit(link["href"])
            self.assertEqual(target.path, metadata["file"])
            self.assertEqual(link["download"], metadata["file"])
            self.assertEqual(parse_qs(target.query)["v"], [mod.version(self.root)])
            self.assertEqual(metadata["sha256"], hashlib.sha256((site / target.path).read_bytes()).hexdigest())
            self.assertEqual(catalog[mod.id], {"name": mod.name, **metadata})

    def test_mobs_only_ship_in_horror_kids_and_crafting_only_in_kit(self):
        kit, horror = MODS[:2]
        with self.packed(kit, "bp") as bp, self.packed(kit, "rp") as rp:
            self.assertFalse(any("toorantula" in path for path in bp.namelist() + rp.namelist()))
            self.assertNotIn("toorantula", rp.read("texts/en_US.lang").decode())
            self.assertIn("blocks/chaos_table.json", bp.namelist())
            self.assertIn("scripts/main.js", bp.namelist())
        with self.packed(horror, "bp") as bp, self.packed(horror, "rp") as rp:
            self.assertFalse(any(path.startswith(("recipes/", "blocks/", "scripts/")) for path in bp.namelist()))
            self.assertNotIn("chaos_table", rp.read("texts/en_US.lang").decode())
            entity = json.loads(bp.read("entities/toorantula_teerantula.json"))["minecraft:entity"]
            identifier = entity["description"]["identifier"]
            self.assertEqual(identifier, "horror_kids:toorantula_teerantula")
            loot = json.loads(bp.read(entity["components"]["minecraft:loot"]["table"]))
            self.assertEqual(loot["pools"][0]["entries"][0]["functions"][1]["id"], identifier)
            client = json.loads(rp.read("entity/toorantula_teerantula.entity.json"))["minecraft:client_entity"]["description"]
            self.assertEqual(client["identifier"], identifier)
            models = [json.loads(rp.read(p)) for p in rp.namelist() if p.startswith("models/entity/")]
            geometries = {g["description"]["identifier"] for model in models for g in model["minecraft:geometry"]}
            self.assertTrue(set(client["geometry"].values()) <= geometries)
            animations = json.loads(rp.read("animations/toorantula_teerantula.animation.json"))["animations"]
            self.assertTrue(set(client["animations"].values()) <= animations.keys())
            controllers = json.loads(rp.read("render_controllers/toorantula_teerantula.render_controllers.json"))["render_controllers"]
            self.assertEqual(set(client["render_controllers"]), controllers.keys())
            self.assertIn(f"entity.{identifier}.name=Toorantula Teerantula", rp.read("texts/en_US.lang").decode())

    def test_each_mod_bumps_independently_and_site_keeps_all(self):
        self.addCleanup(build_site, self.root)
        self.preserve_manifests()
        kit, horror = MODS[:2]
        kit_before = [kit.manifest(self.root, kind) for kind in ("bp", "rp")]
        horror_ids = [horror.manifest(self.root, kind)["header"]["uuid"] for kind in ("bp", "rp")]
        bump(horror, "minor", self.root)
        self.assertEqual(horror.version(self.root), "1.1.0")
        self.assertEqual([kit.manifest(self.root, kind) for kind in ("bp", "rp")], kit_before)
        self.assertEqual([horror.manifest(self.root, kind)["header"]["uuid"] for kind in ("bp", "rp")], horror_ids)
        self.assertEqual(horror.tag(self.root), "horror-kids-v1.1.0")
        self.assertEqual(kit.tag(self.root), "v" + kit.version(self.root))
        bump(kit, "patch", self.root)
        self.assertEqual(kit.version(self.root), "1.3.1")
        self.assertEqual(horror.version(self.root), "1.1.0")
        validate(self.root)
        package(self.root)
        build_site(self.root)
        catalog = json.loads((self.root / "_site/mods.json").read_text())
        self.assertEqual(catalog[kit.id]["version"], "1.3.1")
        self.assertEqual(catalog[horror.id]["version"], "1.1.0")

    def test_horror_kids_includes_both_mobs_and_complete_kraken_resources(self):
        mod = MODS[1]
        with self.packed(mod, "bp") as bp, self.packed(mod, "rp") as rp:
            manifest = json.loads(bp.read("manifest.json"))
            self.assertEqual([m["type"] for m in manifest["modules"]], ["data"])
            self.assertEqual(len(manifest["dependencies"]), 1)
            self.assertFalse(any(p.startswith("spawn_rules/") for p in bp.namelist()))
            self.assertEqual({p for p in bp.namelist() if p.startswith("entities/")},
                             {"entities/kraken.json", "entities/toorantula_teerantula.json"})
            entity = json.loads(bp.read("entities/kraken.json"))["minecraft:entity"]
            self.assertEqual(entity["description"]["identifier"], "horror_kids:kraken")
            self.assertNotIn("runtime_identifier", entity["description"])
            components = entity["components"]
            self.assertEqual(components["minecraft:health"], {"value": 600, "max": 600})
            self.assertEqual(components["minecraft:boss"]["name"], "Kraken")
            self.assertEqual(components["minecraft:boss"]["hud_range"], 55)
            breath = components["minecraft:breathable"]
            self.assertTrue(breath["breathes_water"])
            self.assertFalse(breath["breathes_air"])
            self.assertFalse(breath["breathes_lava"])
            self.assertEqual(breath["total_supply"], 15)
            self.assertGreaterEqual(breath["suffocate_time"], 0)
            navigation = components["minecraft:navigation.swim"]
            self.assertTrue(navigation["can_swim"])
            self.assertFalse(navigation["can_walk"])
            self.assertFalse(navigation["can_breach"])
            self.assertEqual(components["minecraft:attack"]["effect_name"], "wither")
            self.assertLess(components["minecraft:behavior.melee_attack"]["priority"],
                            components["minecraft:behavior.random_swim"]["priority"])
            self.assertFalse(any(key.startswith("minecraft:behavior.squid_") for key in components))
            self.assertNotIn("minecraft:despawn", components)
            self.assertIn("minecraft:persistent", components)
            json.loads(bp.read(components["minecraft:loot"]["table"]))
            client = json.loads(rp.read("entity/kraken.entity.json"))["minecraft:client_entity"]["description"]
            self.assertEqual(client["identifier"], entity["description"]["identifier"])
            model = json.loads(rp.read("models/entity/kraken.geo.json"))["minecraft:geometry"][0]
            self.assertEqual(client["geometry"]["default"], model["description"]["identifier"])
            bones = {bone["name"] for bone in model["bones"]}
            self.assertEqual(len([name for name in bones if name.startswith("tentacle")]), 24)
            for bone in model["bones"]:
                if "parent" in bone:
                    self.assertIn(bone["parent"], bones)
            animations = json.loads(rp.read("animations/kraken.animation.json"))["animations"]
            for name in client["animations"].values():
                self.assertTrue(animations[name]["bones"].keys() <= bones)
                self.assertNotIn("variable.squid", json.dumps(animations[name]))
            texture = rp.read(client["textures"]["default"] + ".png")
            self.assertEqual(texture[:8], b"\x89PNG\r\n\x1a\n")
            controllers = json.loads(rp.read("render_controllers/kraken.render_controllers.json"))["render_controllers"]
            self.assertTrue(set(client["render_controllers"]) <= controllers.keys())
            self.assertIn("entity.horror_kids:kraken.name=Kraken", rp.read("texts/en_US.lang").decode())
        for other in MODS[:1]:
            with self.packed(other, "bp") as pack:
                self.assertFalse(any("kraken" in path for path in pack.namelist()))

    def test_duplicate_identities_and_cross_mod_dependencies_are_rejected(self):
        self.preserve_manifests()
        kit, horror = MODS[:2]
        path = horror.pack_dir(self.root, "bp") / "manifest.json"
        original = horror.manifest(self.root, "bp")
        manifest = json.loads(json.dumps(original))
        manifest["header"]["uuid"] = kit.manifest(self.root, "bp")["header"]["uuid"]
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate(self.root)
        manifest = json.loads(json.dumps(original))
        manifest["dependencies"][0]["uuid"] = kit.manifest(self.root, "rp")["header"]["uuid"]
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "dependencies differ"):
            validate(self.root)

    def test_rebuilding_removes_stale_files_from_existing_archive(self):
        kit = MODS[0]
        archive = self.root / "dist" / f"{kit.package}-BP-{kit.version(self.root)}.mcpack"
        with ZipFile(archive, "a") as pack:
            pack.writestr("entities/removed_mob.json", "{}")
        package(self.root)
        with self.packed(kit, "bp") as pack:
            self.assertNotIn("entities/removed_mob.json", pack.namelist())


if __name__ == "__main__":
    unittest.main()
