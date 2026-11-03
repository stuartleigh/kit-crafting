"""Build independently versioned Minecraft add-ons using only Python's stdlib."""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Mod:
    id: str
    name: str
    package: str
    directory: str
    dev_name: str
    tag_prefix: str
    script_dependencies: tuple = ()

    def pack_dir(self, root, kind):
        return root / f"{self.directory}_{kind}"

    def manifest(self, root, kind):
        return json.loads((self.pack_dir(root, kind) / "manifest.json").read_text())

    def version(self, root):
        return ".".join(map(str, self.manifest(root, "bp")["header"]["version"]))

    def tag(self, root):
        return self.tag_prefix + self.version(root)


MODS = (
    Mod("kit-crafting", "Kit Crafting", "Kit-Crafting", "kit_crafting", "KitCrafting", "v",
        (("@minecraft/server", "2.0.0"),)),
    Mod("horror-kids", "Horror Kids", "Horror-Kids", "horror_kids", "HorrorKids", "horror-kids-v"),
)


def validate(root=ROOT):
    uuids = set()
    for mod in MODS:
        bp, rp = (mod.manifest(root, kind) for kind in ("bp", "rp"))
        version = bp["header"]["version"]
        if len(version) != 3 or any(type(n) is not int or n < 0 for n in version):
            raise ValueError(f"{mod.name}: invalid version {version}")
        for kind, pack in (("bp", bp), ("rp", rp)):
            if any(section["version"] != version for section in [pack["header"], *pack["modules"]]):
                raise ValueError(f"{mod.name}: pack/module versions differ")
            for section in [pack["header"], *pack["modules"]]:
                if section["uuid"] in uuids:
                    raise ValueError(f"Duplicate pack/module UUID: {section['uuid']}")
                uuids.add(section["uuid"])
            for path in mod.pack_dir(root, kind).rglob("*.json"):
                json.loads(path.read_text())
        expected = [{"uuid": rp["header"]["uuid"], "version": version}]
        expected += [{"module_name": name, "version": ver} for name, ver in mod.script_dependencies]
        if bp.get("dependencies", []) != expected:
            raise ValueError(f"{mod.name}: resource/script dependencies differ")


def write_zip(path, entries):
    """Rebuild archives so moved/deleted files cannot survive from an older build."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    with ZipFile(temporary, "w", ZIP_DEFLATED) as archive:
        for source, name in entries:
            archive.write(source, name)
    temporary.replace(path)


def package(root=ROOT):
    validate(root)
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    for mod in MODS:
        packs = []
        for kind in ("bp", "rp"):
            directory = mod.pack_dir(root, kind)
            output = dist / f"{mod.package}-{kind.upper()}-{mod.version(root)}.mcpack"
            write_zip(output, ((p, p.relative_to(directory).as_posix())
                               for p in sorted(directory.rglob("*"))
                               if p.is_file() and p.name != ".DS_Store" and not p.name.endswith(".tmp")))
            packs.append(output)
        addon = dist / f"{mod.package}-{mod.version(root)}.mcaddon"
        write_zip(addon, ((p, p.name) for p in packs))
        print(f"Built {addon}")


def bump(mod, part, root=ROOT):
    validate(root)
    version = mod.manifest(root, "bp")["header"]["version"]
    index = ("major", "minor", "patch").index(part)
    version[index] += 1
    version[index + 1:] = [0] * (2 - index)
    for kind in ("bp", "rp"):
        manifest = mod.manifest(root, kind)
        for section in [manifest["header"], *manifest["modules"]]:
            section["version"] = version
        for dependency in manifest.get("dependencies", []):
            if "uuid" in dependency:
                dependency["version"] = version
        (mod.pack_dir(root, kind) / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{mod.name} version bumped to {mod.version(root)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "package", "version", "tag", "install-dev",
                                            "bump-patch", "bump-minor", "bump-major"))
    parser.add_argument("--mod", choices=[m.id for m in MODS], default="kit-crafting")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    mod = next(m for m in MODS if m.id == args.mod)
    if args.command == "validate":
        validate()
    elif args.command == "package":
        subprocess.run(["python3", str(ROOT / "scripts/generate_chaos.py"), "--check"], check=True)
        package()
    elif args.command == "version":
        print(mod.version(ROOT))
    elif args.command == "tag":
        print(mod.tag(ROOT))
    elif args.command.startswith("bump-"):
        bump(mod, args.command.removeprefix("bump-"))
    elif args.command == "install-dev":
        if args.data_dir is None:
            parser.error("install-dev requires --data-dir")
        for addon in MODS:
            for kind, folder, suffix in (("bp", "development_behavior_packs", ""),
                                         ("rp", "development_resource_packs", "-Resources")):
                destination = args.data_dir / folder / (addon.dev_name + suffix)
                destination.mkdir(parents=True, exist_ok=True)
                subprocess.run(["rsync", "-a", "--delete", str(addon.pack_dir(ROOT, kind)) + "/",
                                str(destination) + "/"], check=True)
                print(f"Installed {destination}")


if __name__ == "__main__":
    main()
