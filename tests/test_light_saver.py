"""Offline Light Saver combat-filter and packaged-model regression checks."""
from io import BytesIO
import json
from pathlib import Path
import shutil
import struct
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from packs import MODS, ROOT, package


def matches_filter(rule, families, has_health=True):
    if "all_of" in rule:
        return all(matches_filter(child, families, has_health) for child in rule["all_of"])
    assert rule["subject"] == "other"
    if rule["test"] == "has_component":
        assert rule["value"] == "minecraft:health"
        result = has_health
    elif rule["test"] == "is_family":
        result = rule["value"] in families
    else:
        raise AssertionError("Unexpected targeting filter: " + str(rule))
    return not result if rule.get("operator") == "!=" else result


class LightSaverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entity = json.loads((ROOT / "horror_kids_bp/entities/light_saver.json").read_text())["minecraft:entity"]
        cls.components = cls.entity["components"]

    def test_all_combat_target_types_except_light_savers(self):
        components = self.components
        for goal in ("nearest_attackable_target", "hurt_by_target"):
            rules = components["minecraft:behavior." + goal]["entity_types"]
            for families in ({"player"}, {"chicken", "mob"}, {"villager", "mob"},
                             {"zombie", "monster", "mob"}, {"vex", "monster", "mob"},
                             {"kraken", "monster", "mob"}, {"dragon", "monster", "mob"},
                             {"toorantula", "monster", "mob"}, {"unknown_custom_mob"}):
                with self.subTest(goal=goal, families=families):
                    self.assertTrue(any(matches_filter(r["filters"], families) for r in rules))
            family = set(components["minecraft:type_family"]["family"])
            self.assertFalse(any(matches_filter(r["filters"], family) for r in rules))
            for families in ({"item"}, {"projectile"}, {"xp_orb"}):
                self.assertFalse(any(matches_filter(r["filters"], families, False) for r in rules))

    def test_native_vex_flight_charge_and_frail_stats(self):
        c = self.components
        self.assertEqual(self.entity["description"]["runtime_identifier"], "minecraft:vex")
        self.assertEqual(c["minecraft:physics"], {"has_collision": False, "has_gravity": False})
        self.assertIn("minecraft:movement.basic", c)
        self.assertIn("minecraft:navigation.walk", c)
        charge = c["minecraft:behavior.charge_attack"]
        self.assertGreater(charge["success_rate"], 0)
        self.assertGreater(charge["speed_multiplier"], 1)
        self.assertEqual(charge["min_distance"], 0)
        self.assertGreaterEqual(charge["max_distance"], c["minecraft:follow_range"]["value"])
        self.assertLess(c["minecraft:behavior.nearest_attackable_target"]["priority"], charge["priority"])
        self.assertEqual(c["minecraft:health"], {"value": 8, "max": 8})
        self.assertEqual(c["minecraft:attack"]["damage"], 6)
        self.assertNotIn("minecraft:equipment", c)  # No accidental sword damage bonus.
        self.assertNotIn("minecraft:burns_in_daylight", c)
        self.assertNotIn("minecraft:timer", c)

    def test_packaged_resources_and_two_scaled_swords(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for addon in MODS:
            for kind in ("bp", "rp"):
                shutil.copytree(addon.pack_dir(ROOT, kind), addon.pack_dir(root, kind))
        package(root)
        mod = MODS[1]
        def packed(addon, kind):
            with ZipFile(root / "dist" / f"{addon.package}-{addon.version(root)}.mcaddon") as outer:
                self.assertIsNone(outer.testzip())
                data = outer.read(f"{addon.package}-{kind.upper()}-{addon.version(root)}.mcpack")
            return ZipFile(BytesIO(data))
        with packed(mod, "bp") as bp, packed(mod, "rp") as rp:
            client = json.loads(rp.read("entity/light_saver.entity.json"))["minecraft:client_entity"]["description"]
            self.assertEqual(client["identifier"], self.entity["description"]["identifier"])
            self.assertIn("entities/light_saver.json", bp.namelist())
            self.assertEqual(float(client["scripts"]["scale"]), 0.6)
            model = json.loads(rp.read("models/entity/light_saver.geo.json"))["minecraft:geometry"][0]
            self.assertEqual(model["description"]["identifier"], client["geometry"]["default"])
            bones = {b["name"]: b for b in model["bones"]}
            for bone in bones.values():
                if "parent" in bone:
                    self.assertIn(bone["parent"], bones)
            for side in ("left", "right"):
                sword = bones[side + "_sword"]
                self.assertEqual(sword["parent"], side + "arm")
                self.assertGreaterEqual(len(sword["cubes"]), 4)
            body_cubes = [cube for name, bone in bones.items() if not name.endswith("_sword")
                          for cube in bone.get("cubes", [])]
            lowest = min(c["origin"][1] for c in body_cubes)
            highest = max(c["origin"][1] + c["size"][1] for c in body_cubes)
            self.assertAlmostEqual((highest - lowest) / 16 * 0.6,
                                   self.components["minecraft:collision_box"]["height"])
            animations = json.loads(rp.read("animations/light_saver.animation.json"))["animations"]
            for name in client["animations"].values():
                self.assertTrue(animations[name]["bones"].keys() <= bones.keys())
                self.assertIn("query.is_charging", json.dumps(animations[name]))
            controllers = json.loads(rp.read("render_controllers/light_saver.render_controllers.json"))["render_controllers"]
            self.assertTrue(set(client["render_controllers"]) <= controllers.keys())
            texture = rp.read(client["textures"]["default"] + ".png")
            self.assertEqual(texture[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", texture[16:24]),
                             (model["description"]["texture_width"], model["description"]["texture_height"]))
            self.assertIn("entity.horror_kids:light_saver.name=The Light Saver", rp.read("texts/en_US.lang").decode())
        with packed(MODS[0], "bp") as bp:
            self.assertNotIn("entities/light_saver.json", bp.namelist())


if __name__ == "__main__":
    unittest.main()
