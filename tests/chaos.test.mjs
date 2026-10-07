import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { chooseReward, excludedItemIds, inventorySlot } from "../kit_crafting_bp/scripts/chaos_logic.js";
import { CHOICE_PROPERTY, redeemSlot } from "../kit_crafting_bp/scripts/chaos_runtime.js";
import { REWARDS } from "../kit_crafting_bp/scripts/chaos_rewards.js";

const pool = ["minecraft:stick", "minecraft:diamond_sword", "minecraft:netherite_chestplate"];

test("exact 50/50 boundary and equal selection across the random pool", () => {
    assert.equal(chooseReward([pool[0]], pool, () => 0.499999), "normal");
    for (const [draw, expected] of [[0, pool[1]], [0.4999, pool[1]], [0.5, pool[2]], [0.9999, pool[2]]]) {
        const draws = [0.5, draw];
        assert.equal(chooseReward([pool[0]], pool, () => draws.shift()), expected);
    }
});

test("sticks can become netherite armour and expensive swords can become sticks", () => {
    assert.equal(chooseReward([pool[0]], pool, () => 0.9), pool[2]);
    const draws = [0.5, 0];
    assert.equal(chooseReward([pool[1]], pool, () => draws.shift()), pool[0]);
});

test("metadata aliases cannot sneak the intended output into the random branch", () => {
    assert.deepEqual(excludedItemIds({item: "minecraft:dye", data: 4}), ["minecraft:dye", "minecraft:lapis_lazuli"]);
});

test("inventory replacement targets the correct hotbar/main inventory slots", () => {
    assert.equal(inventorySlot(0), "slot.hotbar 0");
    assert.equal(inventorySlot(8), "slot.hotbar 8");
    assert.equal(inventorySlot(9), "slot.inventory 0");
    assert.equal(inventorySlot(35), "slot.inventory 26");
    assert.throws(() => inventorySlot(36));
});

class Stack {
    constructor(typeId, amount = 1) { this.typeId = typeId; this.amount = amount; this.properties = {}; }
    getDynamicProperty(key) { return this.properties[key]; }
    setDynamicProperty(key, value) { this.properties[key] = value; }
    clone() { const copy = new Stack(this.typeId, this.amount); copy.properties = {...this.properties}; return copy; }
}

function fixture() {
    const recipe = JSON.parse(readFileSync(new URL("../kit_crafting_bp/recipes/chaos/minecraft_stick.json", import.meta.url)));
    const id = recipe["minecraft:recipe_shaped"].result.item;
    const slots = new Map([[12, new Stack(id)]]);
    const container = {
        getItem: slot => slots.get(slot)?.clone(),
        setItem: (slot, item) => slots.set(slot, item?.clone()),
    };
    return {id, container, slots};
}

test("normal batch produces four sticks in the same occupied slot", () => {
    const {container} = fixture();
    const player = {runCommand(command) {
        assert.match(command, /^loot replace entity @s slot.inventory 3 1 loot "kit_crafting\/chaos\/normal_/);
        container.setItem(12, new Stack("minecraft:stick", 4));
    }};
    assert.equal(redeemSlot(player, container, 12, REWARDS, pool, Stack, () => 0), true);
    assert.equal(container.getItem(12).amount, 4);
    assert.equal(redeemSlot(player, container, 12, REWARDS, pool, Stack), false);
});

test("full inventories need no free slot for a random reward", () => {
    const {container} = fixture();
    redeemSlot({}, container, 12, REWARDS, pool, Stack, () => 0.9);
    assert.equal(container.getItem(12).typeId, "minecraft:netherite_chestplate");
    assert.equal(container.getItem(12).amount, 1);
});

test("failed normal delivery retains the token and its original roll on retry", () => {
    const {id, container} = fixture();
    const player = {runCommand() { container.setItem(12, undefined); throw new Error("failed loot"); }};
    assert.throws(() => redeemSlot(player, container, 12, REWARDS, pool, Stack, () => 0));
    assert.equal(container.getItem(12).typeId, id);
    assert.equal(container.getItem(12).getDynamicProperty(CHOICE_PROPERTY), "normal");
    player.runCommand = () => container.setItem(12, new Stack("minecraft:stick", 4));
    redeemSlot(player, container, 12, REWARDS, pool, Stack, () => { throw new Error("must not reroll"); });
    assert.equal(container.getItem(12).typeId, "minecraft:stick");
});

test("generated normal loot preserves quantities, coloured variants and bottle returns", () => {
    const whiteBanner = Object.values(REWARDS).find(r => r.item === "minecraft:banner" && r.data === 15);
    assert.ok(whiteBanner);
    const loot = JSON.parse(readFileSync(new URL(`../kit_crafting_bp/loot_tables/${whiteBanner.loot}.json`, import.meta.url)));
    assert.deepEqual(loot.pools[0].entries[0].functions, [{function:"set_data",data:15},{function:"set_count",count:1}]);
    const honey = JSON.parse(readFileSync(new URL("../kit_crafting_bp/recipes/chaos/minecraft_honey_block.json", import.meta.url)));
    assert.deepEqual(honey["minecraft:recipe_shaped"].result[1], {item:"minecraft:glass_bottle",count:4,data:0});
});
