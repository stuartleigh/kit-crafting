"""Build a self-contained download site and verify pack version relationships."""
import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parent.parent
bp = json.loads((root / "kit_crafting_bp/manifest.json").read_text())
rp = json.loads((root / "kit_crafting_rp/manifest.json").read_text())
version = bp["header"]["version"]
assert rp["header"]["version"] == version, "Pack versions differ"
for pack in (bp, rp):
    assert all(m["version"] == version for m in pack["modules"]), "Module versions differ"
assert [d for d in bp["dependencies"] if "uuid" in d] == [{"uuid": rp["header"]["uuid"], "version": version}], "Resource dependency differs"
assert [d for d in bp["dependencies"] if "module_name" in d] == [{"module_name": "@minecraft/server", "version": "2.0.0"}], "Script dependency differs"
version_text = ".".join(map(str, version))
source = root / "dist" / f"Kit-Crafting-{version_text}.mcaddon"
site = root / "_site"
site.mkdir(exist_ok=True)
shutil.copyfile(source, site / "Kit-Crafting.mcaddon")
digest = hashlib.sha256(source.read_bytes()).hexdigest()
(site / "version.json").write_text(json.dumps({"version": version_text, "file": "Kit-Crafting.mcaddon", "sha256": digest}, indent=2) + "\n")
(site / "index.html").write_text((root / "site/index.html").read_text().replace("{{VERSION}}", version_text))
(site / ".nojekyll").touch()
print(f"Built download site for {version_text} ({digest})")
