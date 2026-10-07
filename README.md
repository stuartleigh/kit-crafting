# Kit Crafting

Minecraft Education behavior packs for version 26.32.

The add-on has a behavior pack in `kit_crafting_bp/` and a resource pack in
`kit_crafting_rp/`. Add future recipes to `kit_crafting_bp/recipes/`.

## Recipes

### Chaos Crafting Table

Combine **one crafting table and one amethyst shard**, in any arrangement, to
make a Chaos Crafting Table. Place it and use the usual 3×3 crafting grid.

Every craft spends the normal ingredients and rolls independently:

- **50%:** the normal output, including its normal quantity.
- **50%:** one random inventory item from the game's registered item types,
  excluding the intended output type, air and the internal Chaos Results.

All recipes use the same random pool. Sticks can turn into netherite armour;
diamond swords can turn into sticks. There are no value tiers. Bucket and bottle
returns still happen on either outcome.

The output preview shows **Chaos Result (reveals in inventory)**. Move it into
your inventory (or close the crafting screen) and it automatically becomes the
reward within a quarter of a second. Each Chaos Result represents one craft and
does not stack. A full inventory works if the result can occupy a slot; a result
held on the cursor waits until you put it in a slot. The roll is saved before
delivery, so a failed delivery cannot be used to reroll it. Ordinary crafting
tables retain their ordinary recipes.

The current generated set contains 1,186 bundled Education 26.32 shaped/shapeless
crafting recipe definitions plus Kit Crafting's four recipes. This is a pinned
recipe set, not automatic discovery of other add-ons or engine-only special
recipes such as tool repair and arbitrary fireworks. Some bundled definitions
may depend on game features unavailable in a particular world.

The table requires the stable `@minecraft/server` 2.0.0 scripting module.
No experimental Script API is used. Verified in Education 26.32: the table
registers and opens, consumes ingredients, and reveals normal and random rewards
in inventory. The stick recipe produced four sticks, a golden hoe and a spider
eye in separate crafts. Automated checks cover generated data and reward
transactions; the full recipe set has not been individually tested in-game.

### Blast furnace

The first recipe produces one blast furnace at a crafting table:

```text
I I I
I C I
I F I
```

- `I`: Iron Ingot
- `C`: Fire Charge
- `F`: Furnace

### Iron pickaxe

This alternative recipe produces one iron pickaxe:

```text
I I I
I S I
. S .
```

- `I`: Iron Ingot
- `S`: Stick
- `.`: Empty slot

### Netherite stairs

Netherite stairs use the normal six-block stair pattern and yield four stairs:

```text
N . .
N N .
N N N
```

- `N`: Netherite Block

## Build, version, and install

The Makefile requires `jq`, `zip`, `unzip`, and `rsync`; publishing also uses
Python 3 and Git. Development happens on the Mac; the Windows laptop needs
only Minecraft Education and a browser.

```sh
make                 # validate and build the current version
make install-dev     # update Minecraft's single development copy
make chaos           # regenerate chaos copies after adding/editing recipes
make test            # check reward logic and inventory transactions (Node 20+)
make version         # print the current manifest version
make bump-patch      # 1.0.1 -> 1.0.2
make bump-minor      # 1.0.1 -> 1.1.0
make bump-major      # 1.0.1 -> 2.0.0
make release-patch   # bump patch and immediately build
make release-minor   # bump minor and immediately build
make release-major   # bump major and immediately build
```

Version bumps update both packs' manifest header and module versions. `make`
builds `dist/Kit-Crafting-<version>.mcaddon`, which contains both packs for one
step import into Minecraft Education.

## Development workflow

Use `make install-dev` while developing instead of importing each `.mcpack`.
It synchronizes the source into Minecraft Education's single development pack:

```text
development_behavior_packs/KitCrafting/
development_resource_packs/KitCrafting-Resources/
```

The target deletes stale files only inside that specific development-pack
directory. After installing, leave and re-enter the test world so recipe changes
are reloaded. Keep the manifest version unchanged during ordinary development;
use a `release-*` target when producing a package for distribution.

The default Minecraft data path is for Minecraft Education on macOS. Override it
when necessary:

```sh
make install-dev MINECRAFT_DATA_DIR="/path/to/games/com.mojang"
```

Before switching to this workflow, deactivate imported Kit Crafting versions in
the test world and delete the old imported copies from Minecraft's Storage
screen. Then activate the development copy once.

## Publish updates to Windows

Repository: https://github.com/stuartleigh/kit-crafting

Bookmark: https://stuartleigh.github.io/kit-crafting/

Permanent pack URL: https://stuartleigh.github.io/kit-crafting/Kit-Crafting.mcaddon

Allow `https://stuartleigh.github.io` in Microsoft Family Safety. The page and
download are hosted on that same hostname with no external scripts, fonts,
analytics, or GitHub sign-in. This hostname can also serve other Pages projects
from this personal account. There is no need to allow all of github.com or
all github.io sites. Minecraft's own sign-in/services are separate.

After editing and testing on the Mac:

```sh
make release-patch
git add Makefile README.md kit_crafting_bp kit_crafting_rp scripts site .github .gitignore
git commit -m "Describe the update"
make publish
```

`make publish` checks the build and clean working tree, creates a version tag,
and pushes main and that tag together. The tag starts the GitHub Pages deployment.
Ordinary commits/pushes run checks but do not publish. Check the Actions page for
deployment success before downloading; publication and CDN refresh can take a
few minutes. The download button includes the version to avoid an old cached file.
The stable direct file URL is also available, along with `version.json` containing
the published version and SHA-256 checksum.

Never change the manifest UUIDs for an update. Increase the version for every
published change, including rollbacks (restore the old content in a new version).
Do not delete or move published version tags. If a push fails after a local tag
was created, retry `git push --atomic origin main vX.Y.Z` for that version.
If a deployment fails, fix the cause and rerun the failed workflow in GitHub Actions.

On Windows, save and exit the world, download, and open the `.mcaddon` with
Minecraft Education. Activate both packs on first use. Importing a higher version
updates the installed packs; check the existing world's active versions after
the first upgrade. Back up important worlds before updating. This is a manual
download/import workflow, not a background updater, and requires no GitHub credentials
or development tools on Windows.

## Hosting setup and verification

GitHub Pages must use **GitHub Actions** as its publishing source. The `github-pages`
environment must permit deployment from release tags (`v*`). The repository's
Actions tab shows checks and deployments. No personal access token is stored in
the project: deployment uses GitHub's temporary workflow credentials.

`make site` builds a local preview in `_site/`. `make validate` checks JSON syntax;
the site builder also verifies matching pack/module versions and the resource
dependency. These checks do not validate Minecraft's runtime compatibility.

Netherite Stairs remain experimental: registration has not yet been confirmed
in Minecraft Education, and the current definition has fixed orientation and
full-block collision. Publishing this pack does not resolve that outstanding issue.

The Netherite texture originates from Minecraft's game assets; it is not an
original Kit Crafting asset. No blanket open-source license is granted for it.
