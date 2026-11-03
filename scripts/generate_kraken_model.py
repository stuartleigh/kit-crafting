"""Generate the Kraken's geometry, animation and original pixel texture.

The eight-arm layout takes its cue from Education's squid. This model, UV atlas
and time-based animation are custom: no vanilla textures or squid-only variables
are needed. Generated assets are checked in; normal builds need no generator.
"""
import json
import math
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent.parent
RP = ROOT / "horror_kids_rp"
MODEL = "horror_kids.kraken"
TILE = 16
WIDTH, HEIGHT = 128, 32
# Atlas tiles: mantle, cap, arm, suckers, eye, highlight, beak, fin.
COLORS = [(245, 184, 202), (251, 202, 215), (237, 166, 189), (241, 179, 198),
          (53, 28, 55), (255, 241, 223), (115, 46, 82), (229, 146, 177)]


def write_json(relative, value):
    path = RP / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def write_png(path, width, height, pixels):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    path.parent.mkdir(parents=True, exist_ok=True)
    scanlines = b"".join(b"\0" + bytes(pixels[y * width * 3:(y + 1) * width * 3]) for y in range(height))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(scanlines, 9)) + chunk(b"IEND", b""))


def texture_pixels():
    pixels = bytearray()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            tile = x // TILE
            color = COLORS[tile]
            u, v = x % TILE, y % TILE
            if tile == 3:  # Two columns of pale, darker-rimmed suction cups.
                distance = min((u - cx) ** 2 + (v - cy) ** 2 for cx in (4, 11) for cy in (3, 11))
                color = (255, 225, 216) if distance <= 3 else ((191, 103, 142) if distance <= 8 else color)
            elif tile in (0, 1, 2, 7):
                variation = ((x * 7 + y * 11) % 7) - 3
                if (u * 3 + v * 5) % 37 == 0:
                    variation -= 12
                color = tuple(max(0, min(255, channel + variation)) for channel in color)
            pixels.extend(color)
    return pixels


def cube(origin, size, tile, suckers=False):
    uv = {face: {"uv": [tile * TILE, 0], "uv_size": [TILE, TILE]}
          for face in ("north", "south", "east", "west", "up", "down")}
    if suckers:
        uv["south"] = {"uv": [3 * TILE, 0], "uv_size": [TILE, TILE]}
    return {"origin": origin, "size": size, "uv": uv}


def generate():
    bones = [
        {"name": "swim_orientation", "pivot": [0, 54, 0]},
        {"name": "body", "parent": "swim_orientation", "pivot": [0, 40, 0], "cubes": [
            cube([-10, 38, -10], [20, 32, 20], 0),
            cube([-8, 70, -8], [16, 8, 16], 1),
            cube([-5, 78, -5], [10, 4, 10], 1),
        ]},
        {"name": "beak", "parent": "body", "cubes": [cube([-3, 35, -3], [6, 3, 6], 6)]},
    ]
    for side in (-1, 1):
        # Large side-facing squid eyes with cream glints, and mantle fins.
        x = -10.7 if side < 0 else 10
        bones.append({"name": f"eye_{side}", "parent": "body", "cubes": [
            cube([x, 47, -5], [0.7, 7, 9], 4),
            cube([x - 0.2 if side < 0 else x + 0.7, 51, -3], [0.2, 2, 2], 5),
        ]})
        fin_x = -17 if side < 0 else 9
        bones.append({"name": f"fin_{side}", "parent": "body", "pivot": [side * 9, 68, 0],
                      "rotation": [0, 0, side * 18], "cubes": [cube([fin_x, 67, -7], [8, 2, 14], 7)]})
    # The mantle's long axis is +Y in geometry. A level swim needs -90 degrees
    # of pitch so the mantle leads and the tentacles trail. The client computes
    # the climb/dive angle from native horizontal/vertical speed each frame.
    animated = {"swim_orientation": {"rotation": ["variable.kraken_pitch", 0, 0]},
                "body": {"position": [0, "query.is_in_water ? math.sin(query.life_time * 90) * 1.2 : 0", 0],
                          "rotation": [0, 0, "query.is_in_water ? math.sin(query.life_time * 45) * 3 : 10"]}}
    for index in range(8):
        theta = index * math.pi / 4
        x, z = round(math.sin(theta) * 8, 4), round(-math.cos(theta) * 8, 4)
        # Opposing long grasping arms give the vanilla eight-arm shape a new silhouette.
        lengths = (20, 15, 8) if index in (0, 4) else (17, 12, 6)
        y = 40
        # Keep the radial direction and minimum splay out of the animation's
        # rotation channels. Animating a combined pitch/yaw bone folded the
        # original arms together in-game, which bind-pose previews missed.
        parent = f"tentacle{index + 1}_anchor"
        bones.append({"name": parent, "parent": "body", "pivot": [x, y, z],
                      "rotation": [55, -index * 45, 0]})
        for segment, (length, thickness, curl) in enumerate(zip(lengths, (3.5, 2.5, 1.5), (0, 12, -30))):
            name = f"tentacle{index + 1}_{segment}"
            bone = {"name": name, "parent": parent, "pivot": [x, y, z], "rotation": [0, 0, 0],
                    "cubes": [cube([x - thickness / 2, y - length, z - thickness / 2],
                                   [thickness, length, thickness], 2, suckers=True)]}
            bones.append(bone)
            wave = f"math.sin(query.life_time * (query.has_target ? 160 : 100) + {index * 35 + segment * 40})"
            dry_pitch = -40 if segment == 0 else 0
            animated[name] = {"rotation": [f"query.is_in_water ? {curl} + {wave} * {8 if segment < 2 else 12} : {dry_pitch}", 0, 0]}
            y -= length
            parent = name
    # Align the navigation origin with the mantle's base, like vanilla squid.
    # Hanging tentacles should not require a six-block-tall clear water path.
    for bone in bones:
        if "pivot" in bone:
            bone["pivot"][1] -= 38
        for shape in bone.get("cubes", []):
            shape["origin"][1] -= 38
    write_json("models/entity/kraken.geo.json", {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{MODEL}", "texture_width": WIDTH, "texture_height": HEIGHT,
                        "visible_bounds_width": 12, "visible_bounds_height": 10, "visible_bounds_offset": [0, 1, 0]},
        "bones": bones,
    }]})
    write_json("animations/kraken.animation.json", {"format_version": "1.8.0", "animations": {
        f"animation.{MODEL}.swim": {"loop": True, "bones": animated},
    }})
    write_png(RP / "textures/entity/kraken.png", WIDTH, HEIGHT, texture_pixels())
    print("Generated pink Kraken: tapered mantle, eight segmented arms, suction cups and swimming animation.")


if __name__ == "__main__":
    generate()
