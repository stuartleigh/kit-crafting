"""Build all downloads and their version/checksum metadata for GitHub Pages."""
import hashlib
import json
import shutil

from packs import MODS, ROOT, validate


def build_site(root=ROOT):
    validate(root)
    site = root / "_site"
    site.mkdir(exist_ok=True)
    template = (root / "site/index.html").read_text()
    catalog = {}
    for mod in MODS:
        version = mod.version(root)
        source = root / "dist" / f"{mod.package}-{version}.mcaddon"
        filename = f"{mod.package}.mcaddon"
        shutil.copyfile(source, site / filename)
        metadata = {"version": version, "file": filename,
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        catalog[mod.id] = {"name": mod.name, **metadata}
        # Preserve the original Kit Crafting version.json URL and schema.
        metadata_file = "version.json" if mod.id == "kit-crafting" else f"{mod.id}-version.json"
        (site / metadata_file).write_text(json.dumps(metadata, indent=2) + "\n")
        template = template.replace("{{" + mod.id.upper().replace("-", "_") + "_VERSION}}", version)
        print(f"Prepared {mod.name} {version}")
    if "{{" in template:
        raise ValueError("Unresolved site template placeholder")
    (site / "mods.json").write_text(json.dumps(catalog, indent=2) + "\n")
    (site / "index.html").write_text(template)
    (site / ".nojekyll").touch()


if __name__ == "__main__":
    build_site()
