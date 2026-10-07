import { chooseReward, excludedItemIds, inventorySlot } from "./chaos_logic.js";

export const CHOICE_PROPERTY = "kit_crafting:chaos_choice";

// Dependencies are supplied by main.js so the transaction can be tested without
// launching Minecraft. Sealed results are deliberately unstackable.
export function redeemSlot(player, container, slot, rewards, itemIds, ItemStack, random = Math.random) {
    let token = container.getItem(slot);
    const reward = token && rewards[token.typeId];
    if (!reward) return false;
    if (token.amount !== 1) throw new Error("Chaos Results must be unstackable");

    let choice = token.getDynamicProperty(CHOICE_PROPERTY);
    if (choice === undefined) {
        const excluded = excludedItemIds(reward);
        if (reward.data === 0) {
            try { excluded.push(new ItemStack(reward.item, 1).typeId); } catch { /* Legacy loot-only ID. */ }
        }
        choice = chooseReward(excluded, itemIds, random);
        // Save before delivery: a failed command/reconnect cannot reroll a craft.
        token.setDynamicProperty(CHOICE_PROPERTY, choice);
        container.setItem(slot, token);
    }
    if (choice === "normal") {
        try {
            player.runCommand(`loot replace entity @s ${inventorySlot(slot)} 1 loot "${reward.loot}"`);
            const delivered = container.getItem(slot);
            if (!delivered || delivered.typeId === token.typeId) {
                throw new Error(`Normal reward failed: ${reward.item}`);
            }
        } catch (error) {
            // No items are removed unless a reward was actually delivered.
            container.setItem(slot, token);
            throw error;
        }
    } else {
        container.setItem(slot, new ItemStack(choice, 1));
    }
    return true;
}
