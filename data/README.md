# Chaos recipe snapshot

`vanilla_crafting_recipes.json` contains the crafting-table shaped/shapeless
recipes bundled with Minecraft Education 26.32 on macOS, merged from its
`Contents/Resources/data/behavior_packs/vanilla*/recipes` directories in version
order. Recipe definitions originate from Minecraft; no blanket open-source
license is granted for that source data.

This checked-in snapshot keeps builds reproducible on Windows and CI without
requiring Minecraft's installation files or a network download. It is not a
live recipe registry: future Minecraft recipes require a refreshed snapshot.
Other add-ons' recipes and engine-only special crafting (for example repairing
tools or arbitrary fireworks) are not discovered automatically.

Run `make chaos` after adding/editing ordinary recipes in
`kit_crafting_bp/recipes/`. The generator includes those recipes, creates
chaos-only copies, hidden unstackable result items, normal-output loot tables
and the runtime lookup. It preserves the original ingredients, patterns,
unlock conditions, priorities and bucket/bottle returns. `make validate`
rejects generated files that are stale.
