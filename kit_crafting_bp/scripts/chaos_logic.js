// One independent roll per craft; the random branch never returns the intended type.
export function chooseReward(excludedIds, itemIds, random = Math.random) {
    if (random() < 0.5) return "normal";
    const eligible = itemIds.filter(id => !excludedIds.includes(id));
    if (eligible.length === 0) throw new Error("No random rewards available");
    return eligible[Math.floor(random() * eligible.length)];
}

export function inventorySlot(slot) {
    if (!Number.isInteger(slot) || slot < 0 || slot >= 36) {
        throw new Error("Invalid player inventory slot");
    }
    return slot < 9 ? `slot.hotbar ${slot}` : `slot.inventory ${slot - 9}`;
}

// Legacy recipe outputs still use these data-driven aliases. Loot tables retain
// their data values; this mapping also excludes the modern ID from random rewards.
export function excludedItemIds(reward) {
    const ids = [reward.item];
    const dyes = ["ink_sac", "red_dye", "green_dye", "cocoa_beans", "lapis_lazuli", "purple_dye", "cyan_dye", "light_gray_dye", "gray_dye", "pink_dye", "lime_dye", "yellow_dye", "light_blue_dye", "magenta_dye", "orange_dye", "bone_meal", "black_dye", "brown_dye", "blue_dye", "white_dye"];
    if (reward.item === "minecraft:dye" && dyes[reward.data]) ids.push(`minecraft:${dyes[reward.data]}`);
    if (reward.item === "minecraft:chest_boat") {
        const woods = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "bamboo", "cherry", "pale_oak"];
        const wood = woods[reward.data];
        if (wood) ids.push(`minecraft:${wood}_${wood === "bamboo" ? "chest_raft" : "chest_boat"}`);
    }
    return ids;
}
