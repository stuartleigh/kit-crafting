"""Generate an original yellow zombie-style humanoid and two built-in gold swords.

Uses the vanilla humanoid proportions, with an original pixel atlas rather than
redistributing a recoloured zombie skin. The client scales the entire skeleton,
including the swords, to 60%; the behavior pack supplies a matching collision box.
"""
import json
from pathlib import Path

from generate_kraken_model import write_png

ROOT = Path(__file__).resolve().parent.parent
RP = ROOT / "horror_kids_rp"
MODEL = "horror_kids.light_saver"
WIDTH, HEIGHT = 128, 16
# Lemon skin, ochre tunic, dark-yellow trousers, gold blade, grip, red eyes,
# pale blade edge, dark facial features. Each tile is 16 by 16 pixels.
COLORS = [(246, 218, 61), (197, 153, 26), (132, 103, 18), (246, 194, 48),
          (100, 64, 13), (235, 24, 30), (255, 239, 151), (94, 67, 13)]


def write_json(relative, value):
    path = RP / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def texture_pixels():
    pixels = bytearray()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            tile = x // 16
            color = COLORS[tile]
            if tile in (0, 1, 2):
                # Small deterministic patches suggest a mottled zombie skin.
                shade = ((x // 2 * 7 + y // 2 * 11) % 7 - 3) * 3
                color = tuple(max(0, min(255, c + shade)) for c in color)
            pixels.extend(color)
    return pixels


def cube(origin, size, tile):
    return {"origin": origin, "size": size, "uv": {
        face: {"uv": [tile * 16, 0], "uv_size": [16, 16]}
        for face in ("north", "south", "east", "west", "up", "down")}}


def generate():
    bones = [
        {"name": "root", "pivot": [0, 16, 0]},
        {"name": "body", "parent": "root", "pivot": [0, 24, 0],
         "cubes": [cube([-4, 12, -2], [8, 12, 4], 1),
                   cube([-2, 21, -2.1], [4, 3, 0.2], 0)]},
        {"name": "head", "parent": "body", "pivot": [0, 24, 0],
         "cubes": [cube([-4, 24, -4], [8, 8, 8], 0),
                   cube([-3.2, 28, -4.1], [2.4, 1.5, 0.2], 7),
                   cube([0.8, 28, -4.1], [2.4, 1.5, 0.2], 7),
                   cube([-1.5, 25.5, -4.1], [3, 0.5, 0.2], 7)]},
        {"name": "eyes", "parent": "head", "cubes": [
            cube([-2.9, 28.2, -4.25], [1.8, 1, 0.2], 5),
            cube([1.1, 28.2, -4.25], [1.8, 1, 0.2], 5)]},
    ]
    for side, x in (("right", -6), ("left", 6)):
        arm = side + "arm"
        bones.append({"name": arm, "parent": "body", "pivot": [x, 22, 0], "cubes": [
            cube([x - 2, 18, -2], [4, 6, 4], 1),
            cube([x - 2, 12, -2], [4, 6, 4], 0)]})
        # Each sword has a brown grip, wide guard, gold blade and pale edge.
        # Parenting to its arm keeps it in the hand throughout both animations.
        bones.append({"name": side + "_sword", "parent": arm, "pivot": [x, 13, -1],
                      "cubes": [
                          cube([x - 0.5, 12.5, -5], [1, 1, 5], 4),
                          cube([x - 1, 12, -0.5], [2, 2, 1], 3),
                          cube([x - 3.5, 12, -6], [7, 2, 1], 3),
                          cube([x - 1.5, 12.5, -16], [3, 1, 10], 3),
                          cube([x - 1.5, 12.4, -16], [0.5, 1.2, 10], 6),
                          cube([x - 0.5, 12.5, -18], [1, 1, 2], 6),
                      ]})
        leg_x = -2 if side == "right" else 2
        bones.append({"name": side + "leg", "parent": "body", "pivot": [leg_x, 12, 0],
                      "cubes": [cube([leg_x - 2, 0, -2], [4, 12, 4], 2)]})

    write_json("models/entity/light_saver.geo.json", {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry." + MODEL, "texture_width": WIDTH,
                        "texture_height": HEIGHT, "visible_bounds_width": 4,
                        "visible_bounds_height": 4, "visible_bounds_offset": [0, 1, 0]},
        "bones": bones}]})
    write_json("animations/light_saver.animation.json", {"format_version": "1.8.0", "animations": {
        "animation." + MODEL + ".fly": {"loop": True, "bones": {
            "root": {"position": [0, "math.sin(query.life_time * 160) * 0.8", 0],
                     "rotation": ["query.is_charging ? 25 : 8", 0, 0]},
            "head": {"rotation": ["math.clamp(query.target_x_rotation, -35, 35)",
                                   "math.clamp(query.target_y_rotation, -50, 50)", 0]},
            "rightarm": {"rotation": ["query.is_charging ? -65 : -15 + math.sin(query.life_time * 130) * 6", 0, 15]},
            "leftarm": {"rotation": ["query.is_charging ? -65 : -15 - math.sin(query.life_time * 130) * 6", 0, -15]},
            "rightleg": {"rotation": ["20 + math.sin(query.life_time * 150) * 10", 0, 5]},
            "leftleg": {"rotation": ["20 - math.sin(query.life_time * 150) * 10", 0, -5]},
        }}}})
    write_png(RP / "textures/entity/light_saver.png", WIDTH, HEIGHT, texture_pixels())
    print("Generated The Light Saver: yellow humanoid, red eyes and two gold swords.")


if __name__ == "__main__":
    generate()
