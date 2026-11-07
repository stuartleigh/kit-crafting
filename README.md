# Kit's Minecraft Mods

Minecraft Education behavior packs for version 26.32.

Two independent add-ons, each with its own behavior pack, resource pack and version:

| Mod | Contents | Source directories |
| --- | --- | --- |
| Kit Crafting | Recipes, Chaos Crafting Table and Netherite Stairs | `kit_crafting_bp/`, `kit_crafting_rp/` |
| Horror Kids | Toorantula Teerantula, the Kraken boss and The Light Saver | `horror_kids_bp/`, `horror_kids_rp/` |

Use either mod on its own or enable both in the same world. Horror Kids does
not require Kit Crafting or its scripting module. Add future recipes to
`kit_crafting_bp/recipes/` and future horror mobs to `horror_kids_bp/entities/`.
All Horror Kids mobs use the `horror_kids:` namespace.

Toorantula now uses the `horror_kids:` namespace. Old Kit Crafting spider entities
and spawn eggs are not migrated; spawn a new Toorantula after switching packs.

## Horror Kids mobs

### The Light Saver

Added in Horror Kids **1.1.0**. A yellow zombie-style humanoid with red eyes
and a small golden sword in each hand. "40% smaller" means a 0.6 visual scale:
about 1.2 blocks tall, with a 0.36 × 1.2 collision/hit box. Both swords are part
of the model and inherit its scale and arm animations. They are visual weapons,
not equipment or additional damage modifiers, and do not drop on death.
The original lemon/ochre pixel atlas gives it mottled skin and yellow clothing;
it does not redistribute a recoloured vanilla skin.

It has **8 HP (4 hearts)** and deals **6 base melee damage** per charge hit,
matching the direct-impact value in Education's bundled ghast fireball. Actual
damage varies with armour and difficulty; this does not add explosion damage.
It awards 5 XP when last hit by a player, with no special item loot.

It uses the `minecraft:vex` runtime and the bundled Vex movement/physics stack
for native flight, wandering, block phasing and charging. The documented
[charge attack goal](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_charge_attack?view=minecraft-bedrock-stable)
allows lunges up to its 24-block target range. The animation leans forward and
raises both swords while charging. It is persistent, manually spawned, and
has no owner, summoned lifespan or natural spawn rules. Unlike a zombie it
does not burn in daylight. Vex runtime inheritance is deliberate here because
its native flight and charge state drive this mob's behavior and animation.

Both proactive targeting and retaliation accept entities with health and
exclude the `light_saver` family. It attacks passive, neutral and hostile mobs,
including the other Horror Kids bosses. Items and projectiles are not combat
targets; Creative/Spectator players and invulnerable entities remain protected
by Minecraft's normal combat rules. There is no player-only target whitelist.

Find **Spawn The Light Saver** in Creative, or use:

```text
/summon horror_kids:light_saver ~ ~ ~
```

`python3 scripts/generate_light_saver_model.py` regenerates its geometry,
animation and original texture. The build checks cover target exclusions,
packaged resources, sword attachment and proportions. **No in-game test was
run on this computer**, as requested. On the kids' laptop, import 1.1.0,
activate both Horror Kids packs, and check the appearance, free flight and
lunges in a Normal test world. Use Survival to check player attacks, then
spawn a chicken, zombie, Vex and another Light Saver: all except the other
Light Saver should be targeted. Check that it can be killed easily and that
both swords stay attached while it turns, charges and takes damage.

### Toorantula Teerantula

The custom model combines **two spiders webbed together**, with two visible
heads (one with green eyes and one with red eyes), sixteen animated legs,
small fangs, and seven cobweb panels binding the
bodies together. The spiders angle apart slightly and their gait is staggered.
It keeps the prototype's **1.5× scale**, with a wider silhouette from the paired
bodies rather than a fixed 3×1×2 target. The 2.1-block-wide by 1.35-block-high
collision box, movement, combat, health and loot are unchanged by the model.
It has **100 health points (50 hearts)**, ten times the first prototype's health.

The model reuses the game's spider skin, glowing-eye material and actual cobweb
texture (`textures/blocks/web`). The cobweb panels use a separate render pass
with a two-sided cutout material so their gaps are transparent. They disappear
when the mob is invisible. The left head's green eyes are separate faces with
an isolated colour overlay, retaining the vanilla spider's emissive eye alpha;
the right head keeps its red eyes. No vanilla definitions are overridden.

The editable Bedrock geometry is in `horror_kids_rp/models/entity/`, with the
matching animation and web render-controller files in the resource pack.
`python3 scripts/generate_toorantula_model.py` regenerates these files from the
model's proportions and panel placements in that script; ordinary builds use
the checked-in JSON and need no extra dependencies. Regenerating overwrites
manual edits to those generated files. Spider proportions, UVs and gait are
adapted from the vanilla Education 26.32 assets; no blanket open-source license
is granted for those assets. This first paired model still needs in-game
verification of the web rendering, leg motion and overall shape.

Find **Spawn Toorantula Teerantula** in the Creative inventory, or enable cheats
in a test world and run:

```text
/summon horror_kids:toorantula_teerantula ~ ~ ~
```

The enlarged spider prototype was confirmed working in-game by the user. It is
persistent so a test specimen can be revisited and does not spawn naturally.

It now seeks visible targets within **16 blocks**, chases them with spider-style
navigation, and performs melee attacks with **10 base damage** and a one-second
cooldown. Damage against players can vary with difficulty, armour, and effects.
It attacks Survival/Adventure players and friendly or neutral mobs, including
chickens, sheep, villagers, goats, fish, pandas, wolves, golems, Endermen,
ordinary piglins, zombified piglins, and zombie nautiluses. Creative/Spectator
players are not ordinary combat targets.

The targeting filter excludes hostile monsters, hoglins, the Ender Dragon,
piglin brutes, other Toorantulas, and inanimate entities. Ordinary spiders and
cave spiders are left alone. Education NPCs are excluded because they are
non-combat characters. There is no unrestricted retaliation goal, so being hit
by a hostile mob does not make it attack that mob. The mob's own `monster`
family lets vanilla defenders recognise it as hostile. These classifications
were checked against the vanilla entity definitions bundled with Education
26.32; other add-ons depend on their own family tags.

With mob loot enabled, each death drops exactly **one Toorantula Teerantula
spawn egg and ten netherite ingots**. Looting does not increase either quantity.
The spawn egg uses `set_actor_id` with the custom entity identifier, rather
than a hardcoded numeric egg value. Combat and drops still need in-game
verification after reloading the updated development pack.

The intended boss design for later stages is:

| Feature | Definition |
| --- | --- |
| Name | Toorantula Teerantula |
| Appearance | Two spiders webbed together |
| Size | Keep the enlarged prototype's imposing scale; exact block dimensions are flexible |
| Purpose | Angry spider boss that attacks friendly and neutral mobs |
| Temperament | Hostile |
| Movement | “The same as a spider when it's digging” — exact digging behaviour to define before implementation |
| Health | 100 health points (50 hearts), increased tenfold from the initial ghast-level health |
| Attack strength | As strong as the Ender Dragon; the first melee implementation uses 10 base damage, without the dragon's special attack mechanics |
| Drops | One of its own spawn eggs and ten netherite ingots per death |

After `make install-dev`, leave and re-enter the test world and check the spawn
egg name, summon command, enlarged model, leg animations, climbing, collision,
and persistence after saving and reopening the world. Test combat on Normal
difficulty in Survival/Adventure: check chickens, sheep, villagers and neutral
mobs are attacked, while a zombie, creeper, hoglin, piglin brute, and a second
Toorantula are ignored. Include a goat, fish, panda, Enderman and baby zombified
piglin to cover the family-tag exceptions. With `doMobLoot` enabled, kill a
Toorantula, collect both drops and use its dropped egg to spawn another one.
Check the Creator Content Log for missing resources or invalid components.
Use `make` to build the current
development `.mcaddon`; use the release workflow below once it is verified.

### Kraken boss

Kraken is included in **Horror Kids**, alongside Toorantula Teerantula. Find
**Spawn Kraken** in Creative inventory, or enable cheats and summon one in a
deep, open ocean:

```text
/summon horror_kids:kraken ~ ~ ~
```

The model is squid-inspired, with a taller tapered mantle, small fins, large
side-facing eyes, and eight three-segment tentacles. Two opposing tentacles are
longer grasping arms. It has an original light-pink pixel texture with cream
suction cups, and a continuous swimming/curling animation that becomes faster
when it has a target. It does not use squid-only animation variables, AI goals,
or a vanilla runtime identifier. No vanilla squid definitions are overridden.
The navigation origin now sits at the mantle's base, and the collision box
covers the body (1.8 wide × 3.5 high) rather than the hanging tentacles. Its
mantle is about 3.4 blocks tall visually; the arms spread out and extend below
it. Use deep, open water with ample room around it for testing. Tentacles have
separate fixed radial joints so animation cannot fold all eight underneath it.

| Stat or behavior | First implementation |
| --- | --- |
| Health | 600 HP / 300 hearts, fixed across difficulties; based on the bundled Education Wither's base health |
| Boss HUD | Named “Kraken” health bar within 55 blocks |
| Attack | 8 base melee damage, plus Wither I for 10 seconds |
| Attack cooldown | 1.5 seconds; armour and difficulty affect actual damage |
| Target range | 32 blocks, with line of sight |
| Targets | Players and fish, squid, dolphins, turtles and axolotls in water; retaliates against underwater attackers except other Krakens |
| Movement | Free swimming and underwater wandering; no walking, flying or deliberate breaching |
| Breathing | A partly submerged body is safe, even with its head above water; 15 seconds fully out of water starts land damage |
| Persistence | No distance despawn; manual spawn only, no natural spawn rules |
| Resistance | Full knockback resistance; not immune to land suffocation |
| Rewards | Exactly 10 raw pork chops (with mob loot enabled); 50 XP when last hit by a player |

This borrows the Wither's base health and boss presentation, with a close-range
Wither-effect attack suited to tentacles. It does not reproduce the Wither's
projectiles, explosions, block breaking, summoning phase or half-health phases.
Health is fixed at 600; it does not reproduce the vanilla Wither's internal
difficulty-based health adjustments. Loot and encounter balance are initial
choices and can be tuned after playing.

`python3 scripts/generate_kraken_model.py` regenerates the checked-in geometry,
animation and original PNG texture using Python's standard library. The design
uses the vanilla squid's eight-arm layout as a reference, with new proportions,
geometry, UVs and texture. Ordinary builds do not regenerate these assets.

The boss uses the documented [boss HUD component](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_boss?view=minecraft-bedrock-stable),
[generic swimming navigation](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_navigation.generic?view=minecraft-bedrock-stable),
fish-style sway movement and gravity-free water physics. Head-based suffocation
is disabled. An `in_water` environment sensor starts a 15-second land timer;
after it expires, `damage_over_time` deals 2 HP each second. Reentering water
cancels the timer/damage and restores swimming physics; gravity applies on land.
Squid's [idle goal is restricted to the vanilla squid](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_squid_idle?view=minecraft-bedrock-stable),
so the Kraken uses general swimming and melee components.

The first laptop test (1.0.0) confirmed spawning and close-range melee, but
found head-at-surface suffocation, bunched tentacles and no pursuit. The user
reported that 1.0.1 works better. Version 1.0.2 adds the pork-chop drop and a
separate orientation joint: native body yaw handles turns, and smoothed pitch
uses `query.ground_speed` and `query.vertical_speed` so the mantle leads while
swimming horizontally, climbing or diving. It holds its last pitch while idle
and returns upright on land. All tentacles inherit the orientation together.
The rendered orientation changes the model, not its navigation/collision box.
Automated checks exercise land/water transitions, motion-angle cases, the
fixed radial joints and exact loot contents. **The new swimming pose still
needs in-game verification.** After `make install-dev`, activate
Horror Kids and Horror Kids Resources and test in Normal Survival with cheats
available:

1. Summon it in deep open water. Check pink skin, eyes, suction cups and all
   eight tentacles. Check that it swims up and down rather than sitting on the
   bottom, and that its large collision box can move through the test area.
2. Approach within 55 blocks; damage it and check that the Kraken health bar
   falls. Move beyond 55 blocks to check the bar disappears.
3. Check it pursues and hits a Survival player in water, applies Wither, and
   attacks nearby fish or squid. Creative/Spectator players should be ignored.
4. Spawn a second Kraken and check they do not attack each other. Return after
   saving/reopening to check persistence.
5. Spawn it with the top of its head above water; check it remains healthy.
   Move it fully onto dry land; after about 15 seconds check that health decreases.
   Put it back in water and check suffocation stops. This is not an instant
   death: a boss-sized health pool takes longer to exhaust than a normal squid.
6. Kill one with mob loot enabled and check exactly 10 raw pork chops and XP. Check the Creator
   Content Log for missing resources, unknown components or Molang errors.

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

Requires Python 3.9+, Node 20+ for tests, Git for publishing, and `rsync` for
development installation. Builds use Python's standard library; no npm install
is needed. Development happens on the Mac; the Windows laptop needs only
Minecraft Education and a browser.

```sh
make                         # validate and build ALL mods
make site                    # build all downloads and the page in _site/
make install-dev             # synchronize all four development packs
make chaos                   # regenerate chaos data after editing recipes
make test                    # reward logic, pack separation and release checks
make version                 # Kit Crafting version
make version MOD=horror-kids  # Horror Kids version
make bump-patch               # bump only Kit Crafting
make bump-minor MOD=horror-kids
make release-patch MOD=horror-kids  # bump Horror Kids, then build all
```

`MOD` defaults to `kit-crafting`. Version bumps and `release-patch`,
`release-minor`, and `release-major` change only the selected mod. Its behavior
and resource pack header/module versions and resource dependency stay in sync;
the other mods' versions stay unchanged. `make` always builds both mods:

- `dist/Kit-Crafting-<version>.mcaddon`
- `dist/Horror-Kids-<version>.mcaddon`

Each `.mcaddon` contains that mod's two `.mcpack` files for one-step import.
Every build recreates its archives, removing files deleted or moved since a
previous build. Manifests have distinct UUIDs so the mods can coexist.

## Development workflow

Use `make install-dev` instead of importing each package while developing. It
synchronizes all source packs into these Minecraft Education directories:

```text
development_behavior_packs/KitCrafting/
development_resource_packs/KitCrafting-Resources/
development_behavior_packs/HorrorKids/
development_resource_packs/HorrorKids-Resources/
```

Stale files are deleted only inside these four development-pack directories.
Leave and re-enter your test world after installation. Activate the behavior
and resource packs for the mods you are testing. Deactivate old imported copies
before switching to development packs. Replace existing prototype spiders with
new Horror Kids spawn eggs or `/summon horror_kids:toorantula_teerantula`.

The default Minecraft data path is for Education on macOS. Override it with:

```sh
make install-dev MINECRAFT_DATA_DIR="/path/to/games/com.mojang"
```

## Publish updates to Windows

Repository: https://github.com/stuartleigh/kit-crafting

Download page: https://stuartleigh.github.io/kit-crafting/

Both downloads are hosted on the same page:

- https://stuartleigh.github.io/kit-crafting/Kit-Crafting.mcaddon
- https://stuartleigh.github.io/kit-crafting/Horror-Kids.mcaddon

Allow `https://stuartleigh.github.io` in Microsoft Family Safety. The page and
all downloads use that hostname, with no external scripts, fonts, analytics,
or GitHub sign-in. Minecraft's own sign-in/services are separate.

After editing and testing, bump the changed mod's version (the initial split
uses Kit Crafting 1.3.0; The Light Saver uses Horror Kids 1.1.0), commit the changes, then
publish from `main`:

```sh
# A future Kit Crafting update:
make release-patch
git add Makefile README.md kit_crafting_bp kit_crafting_rp horror_kids_bp horror_kids_rp scripts tests site .github
git commit -m "Describe the update"
make publish

# A future Horror Kids update:
make release-patch MOD=horror-kids
git add horror_kids_bp horror_kids_rp
git commit -m "Describe the mob update"
make publish MOD=horror-kids

```

`make publish` runs checks, requires a clean working tree on `main`, then pushes
`main` and the selected mod's tag atomically. Kit Crafting uses `vX.Y.Z` tags;
Horror Kids uses `horror-kids-vX.Y.Z`. Either release tag builds and deploys the
complete page with both current downloads. Ordinary
pushes only run checks. If several mods changed, bump each changed mod and
publish once using any changed mod's new tag.

The workflow checks the tag against the selected mod's manifest. Never change a
mod's UUIDs for an update or reuse published version tags. If a push fails after
creating a local tag, retry `git push --atomic origin main <tag>`. Check the
Actions deployment result before downloading; CDN refresh can take a few minutes.

Download links include each mod's version for cache refresh. `_site/mods.json`
lists all versions, filenames and SHA-256 checksums. `version.json` contains
Kit Crafting's metadata; `horror-kids-version.json` contains Horror Kids' metadata.

On Windows, save and exit the world, download the desired `.mcaddon` files,
and open each with Minecraft Education. In world settings activate the selected
mod's Behavior Pack and matching Resources pack. Use updated Kit Crafting 1.3.0
or later alongside Horror Kids; older Kit Crafting releases still include the
prototype spider. Back up important worlds before updating. No development
tools or GitHub account are needed on Windows.

## Hosting setup and verification

GitHub Pages must use **GitHub Actions** as its source. The `github-pages`
environment must allow deployment from both tag patterns: `v*` and
`horror-kids-v*`. The repository's Actions tab shows checks and deployments.
Deployment uses GitHub's temporary workflow credentials.

`make site` builds a local preview in `_site/`. Validation checks JSON syntax,
unique pack/module UUIDs, version consistency and independent resource/script
dependencies. Automated tests inspect nested downloads, mob/resource separation,
model references, independent version bumps, download URLs and checksums.
These checks do not validate Minecraft runtime compatibility. Verify the renamed
Horror Kids and Kraken spawn eggs, summon commands, rendering, combat and loot
in-game, including the Kraken boss bar and land suffocation.

Netherite Stairs remain experimental: registration has not yet been confirmed
in Minecraft Education, and the current definition has fixed orientation and
full-block collision.

The Netherite texture originates from Minecraft's game assets; it is not an
original Kit Crafting asset. No blanket open-source license is granted for it.
