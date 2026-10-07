import { ItemStack, ItemTypes, system, world } from "@minecraft/server";
import { REWARDS } from "./chaos_rewards.js";
import { redeemSlot } from "./chaos_runtime.js";

let itemIds;
const reportedErrors = new Set();

function randomItemPool() {
    // Use the game's registry, including armour, rare items and other add-ons.
    // Internal sealed results and air are the only deliberate exclusions.
    const ids = new Set();
    for (const type of ItemTypes.getAll()) {
        const id = type.id;
        if (id === "minecraft:air" || id.startsWith("kit_crafting:chaos_result_")) continue;
        try {
            const canonical = new ItemStack(id, 1).typeId;
            if (canonical !== "minecraft:air") ids.add(canonical);
        } catch {
            // Some internal types cannot exist as inventory items.
        }
    }
    return [...ids].sort();
}

system.runInterval(() => {
    if (!itemIds) itemIds = randomItemPool();
    for (const player of world.getAllPlayers()) {
        const container = player.getComponent("minecraft:inventory")?.container;
        if (!container) continue;
        for (let slot = 0; slot < container.size; slot++) {
            try {
                redeemSlot(player, container, slot, REWARDS, itemIds, ItemStack);
            } catch (error) {
                const key = `${player.id}:${error}`;
                if (!reportedErrors.has(key)) {
                    reportedErrors.add(key);
                    console.warn(`[Kit Crafting] ${error}`);
                    player.sendMessage("Chaos Result could not open. Your result is saved; check the content log.");
                }
            }
        }
    }
}, 5);
