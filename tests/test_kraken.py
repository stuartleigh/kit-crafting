"""Regressions for the Kraken's surface breathing, swimming and tentacle layout."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Environment:
    """Exercise the declared sensor/event/timer graph without a Minecraft world."""

    def __init__(self, entity):
        self.entity = entity
        self.groups = []
        self.water = True
        self.timer = None

    def components(self):
        result = dict(self.entity["components"])
        for name in self.groups:
            result.update(self.entity["component_groups"][name])
        return result

    def event(self, name):
        self.action(self.entity["events"][name])

    def action(self, action):
        if "filters" in action:
            condition = action["filters"]
            if condition["test"] != "in_water":
                raise AssertionError("Unimplemented test filter")
            if self.water != condition.get("value", True):
                return
        for child in action.get("sequence", []):
            self.action(child)
        for name in action.get("remove", {}).get("component_groups", []):
            if name in self.groups:
                self.groups.remove(name)
                if "minecraft:timer" in self.entity["component_groups"][name]:
                    self.timer = None
        for name in action.get("add", {}).get("component_groups", []):
            if name not in self.groups:
                self.groups.append(name)
            timer = self.entity["component_groups"][name].get("minecraft:timer")
            if timer:
                self.timer = timer["time"]

    def step(self, water, seconds=0):
        self.water = water
        sensor = self.components()["minecraft:environment_sensor"]
        for trigger in sensor["triggers"]:
            if water == trigger["filters"].get("value", True):
                self.event(trigger["event"])
        if self.timer is not None:
            self.timer -= seconds
            if self.timer <= 0:
                timer = self.components()["minecraft:timer"]
                self.timer = None
                self.event(timer["time_down_event"]["event"])


class KrakenTests(unittest.TestCase):
    def setUp(self):
        self.entity = json.loads((ROOT / "horror_kids_bp/entities/kraken.json").read_text())["minecraft:entity"]

    def test_exposed_head_does_not_hurt_a_body_still_in_water(self):
        self.assertTrue(self.entity["components"]["minecraft:breathable"]["breathes_air"])
        state = Environment(self.entity)
        for _ in range(60):
            state.step(water=True, seconds=1)
            self.assertNotIn("minecraft:damage_over_time", state.components())
            self.assertIsNone(state.timer)
            self.assertFalse(state.components()["minecraft:physics"]["has_gravity"])

    def test_land_grace_expires_and_reentering_water_resets_it(self):
        state = Environment(self.entity)
        for _ in range(14):
            state.step(water=False, seconds=1)
            self.assertNotIn("minecraft:damage_over_time", state.components())
            self.assertTrue(state.components()["minecraft:physics"]["has_gravity"])
        state.step(water=False, seconds=1)
        self.assertIn("minecraft:damage_over_time", state.components())
        state.step(water=True)
        self.assertNotIn("minecraft:damage_over_time", state.components())
        self.assertFalse(state.components()["minecraft:physics"]["has_gravity"])
        state.step(water=False, seconds=1)
        self.assertEqual(state.timer, 14)
        state.step(water=True)
        self.assertIsNone(state.timer)
        state.step(water=False, seconds=14)
        self.assertNotIn("minecraft:damage_over_time", state.components())
        state.step(water=False, seconds=1)
        self.assertIn("minecraft:damage_over_time", state.components())

    def test_native_fish_motion_has_room_to_path_and_overrides_wandering_to_attack(self):
        c = self.entity["components"]
        self.assertIn("minecraft:movement.sway", c)
        self.assertNotIn("minecraft:movement.generic", c)
        self.assertFalse(c["minecraft:physics"]["has_gravity"])
        self.assertFalse(c["minecraft:navigation.generic"]["can_sink"])
        self.assertTrue(c["minecraft:navigation.generic"]["can_swim"])
        self.assertLessEqual(c["minecraft:collision_box"]["height"], 3.5)
        self.assertEqual(c["minecraft:behavior.random_swim"]["interval"], 0)
        self.assertLess(c["minecraft:behavior.melee_attack"]["priority"],
                        c["minecraft:behavior.random_swim"]["priority"])
        self.assertTrue(c["minecraft:behavior.melee_attack"]["track_target"])

    def test_animation_cannot_zero_the_eight_fixed_outward_joints(self):
        model = json.loads((ROOT / "horror_kids_rp/models/entity/kraken.geo.json").read_text())["minecraft:geometry"][0]
        bones = {bone["name"]: bone for bone in model["bones"]}
        animations = json.loads((ROOT / "horror_kids_rp/animations/kraken.animation.json").read_text())["animations"]
        anchors = [bones[f"tentacle{i}_anchor"] for i in range(1, 9)]
        self.assertEqual({a["rotation"][1] % 360 for a in anchors}, set(range(0, 360, 45)))
        self.assertTrue(all(a["rotation"][0] >= 55 for a in anchors))
        self.assertEqual(bones["body"]["cubes"][0]["origin"][1], 0)
        for anchor in anchors:
            self.assertEqual(anchor["parent"], "body")
            first_segment = bones[anchor["name"].replace("_anchor", "_0")]
            self.assertEqual(first_segment["parent"], anchor["name"])
            for animation in animations.values():
                self.assertNotIn(anchor["name"], animation["bones"])
                self.assertNotIn("this", json.dumps(animation["bones"][first_segment["name"]]))


if __name__ == "__main__":
    unittest.main()
