"""Build the paired-spider model with standard-library Python only.

Spider proportions, UVs and gait are adapted from Minecraft Education 26.32's
vanilla spider geometry and animations. Textures remain references to the game.
Generated JSON is checked in; ordinary pack builds do not run this script.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RP = ROOT / "kit_crafting_rp"
MODEL = "kit_crafting.toorantula_teerantula"


def write(relative, value):
    path = RP / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def geometry(identifier, bones, texture_size):
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": identifier,
                "texture_width": texture_size[0],
                "texture_height": texture_size[1],
                "visible_bounds_width": 6,
                "visible_bounds_height": 3,
                "visible_bounds_offset": [0, 1, 0],
            },
            "bones": bones,
        }],
    }


bones = []
poses, walking, looking = {}, {}, {}
for side, dx, dz, yaw, phase in [
    ("left", -6, -1, 12, 0),
    ("right", 6, 1, -12, 90),
]:
    root = f"{side}_root"
    body = f"{side}_body"
    bones.append({"name": root, "pivot": [dx, 9, dz], "rotation": [0, yaw, 0]})
    for name, parent, origin, size, pivot, uv in [
        (body, root, [-3, 6, -3], [6, 6, 6], [0, 9, 0], [0, 0]),
        (f"{side}_head", body, [-4, 5, -11], [8, 8, 8], [0, 9, -3], [32, 4]),
        (f"{side}_abdomen", body, [-5, 5, 3], [10, 8, 12], [0, 9, 9], [0, 12]),
    ]:
        bones.append({
            "name": name, "parent": parent,
            "pivot": [pivot[0] + dx, pivot[1], pivot[2] + dz],
            "cubes": [{"origin": [origin[0] + dx, origin[1], origin[2] + dz],
                       "size": size, "uv": uv}],
        })
    # Small extra mandibles make both heads readable from the front.
    bones.append({
        "name": f"{side}_fangs", "parent": f"{side}_head",
        "pivot": [dx, 6, dz - 10],
        "cubes": [
            {"origin": [dx + x, 3.5, dz - 12.5], "size": [1.5, 3, 2], "uv": [18, 0]}
            for x in [-3, 1.5]
        ],
    })
    looking[f"{side}_head"] = {
        "rotation": ["query.target_x_rotation", "math.clamp(query.target_y_rotation, -35, 35)", 0]
    }
    for i in range(8):
        name = f"{side}_leg{i}"
        sign = -1 if i % 2 == 0 else 1
        row = i // 2
        z = 2 - row
        inner = (side == "left" and sign == 1) or (side == "right" and sign == -1)
        length = 12 if inner else 16
        origin_x = -3 - length if sign == -1 else 3
        bones.append({
            "name": name, "parent": body,
            "pivot": [dx + sign * 4, 9, dz + z],
            "cubes": [{"origin": [dx + origin_x, 8, dz + z - 1],
                       "size": [length, 2, 2], "uv": [18, 0], "mirror": sign == 1}],
        })
        y_angle = [45, 22.5, -22.5, -45][row] * -sign
        z_angle = [45, 33.3, 33.3, 45][row] * sign
        poses[name] = {"rotation": [0, f"{y_angle} - this", f"{z_angle} - this"]}
        offset = row * 90 + phase
        walking[name] = {"rotation": [
            0,
            f"{'-' if sign == -1 else ''}math.abs(math.cos(query.anim_time * 76.34 + {offset}) * 22.92)",
            f"{'-' if sign == 1 else ''}math.abs(math.sin(query.anim_time * 38.17 + {offset}) * 22.92)",
        ]}

# Cover the left head's red eye texels with slightly offset green eye faces.
# Their UVs retain the spider texture's emissive alpha, so no recoloured copy
# of the game texture is needed. The green render pass colours only this bone.
eye_faces = []
dx, dz = -6, -1
for v, columns in [
    (12, [41, 46]), (13, [42, 45]), (14, [40, 47]),
    (15, [40, 42, 43, 44, 45, 47]), (16, [42, 43, 44, 45]),
]:
    for u in columns:
        eye_faces.append({
            "origin": [dx + 43 - u, 24 - v, dz - 11.02],
            "size": [1, 1, 0],
            "uv": {"north": {"uv": [u, v], "uv_size": [1, 1]}},
        })
for x, face, u in [(dx - 4.02, "west", 39), (dx + 4.02, "east", 48)]:
    eye_faces.append({
        "origin": [x, 9, dz - 11], "size": [0, 2, 1],
        "uv": {face: {"uv": [u, 14], "uv_size": [1, 2]}},
    })
bones.append({
    "name": "left_green_eyes", "parent": "left_head",
    "pivot": [dx, 9, dz - 3], "cubes": eye_faces,
})

write("models/entity/toorantula_teerantula.geo.json", geometry(f"geometry.{MODEL}", bones, [64, 32]))
write("animations/toorantula_teerantula.animation.json", {
    "format_version": "1.8.0",
    "animations": {
        f"animation.{MODEL}.default_leg_pose": {"loop": True, "bones": poses},
        f"animation.{MODEL}.look_at_target": {"loop": True, "bones": looking},
        f"animation.{MODEL}.walk": {
            "loop": True, "anim_time_update": "query.modified_distance_moved", "bones": walking,
        },
    },
})

# A separate geometry uses the cobweb's own 16x16 UV space. This keeps the
# vanilla spider texture (including its glowing eyes) independent of web alpha.
webs = []
for name, origin, size, pivot, rotation, face in [
    ("front", [-9, 6, -1], [18, 9, 0], [0, 10, -1], [0, 0, 8], "north"),
    ("back", [-12, 5, 14], [24, 10, 0], [0, 10, 14], [0, 0, -6], "north"),
    ("top_left", [-13, 13.4, 1], [14, 0, 16], [-6, 13.4, 9], [0, 0, -15], "up"),
    ("top_right", [-1, 13.8, 2], [14, 0, 16], [6, 13.8, 10], [0, 0, 15], "up"),
    ("centre", [0, 5, -1], [0, 10, 18], [0, 10, 8], [0, 0, 0], "east"),
    ("wrap_left", [-11, 5, 2], [0, 9, 13], [-11, 9, 8], [0, 0, 25], "east"),
    ("wrap_right", [11, 5, 3], [0, 9, 13], [11, 9, 9], [0, 0, -25], "east"),
]:
    webs.append({
        "name": f"web_{name}", "pivot": pivot, "rotation": rotation,
        "cubes": [{"origin": origin, "size": size,
                   "uv": {face: {"uv": [0, 0], "uv_size": [16, 16]}}}],
    })
write("models/entity/toorantula_teerantula_web.geo.json", geometry(f"geometry.{MODEL}.web", webs, [16, 16]))
write("render_controllers/toorantula_teerantula.render_controllers.json", {
    "format_version": "1.8.0",
    "render_controllers": {
        f"controller.render.{MODEL}.body": {
            "arrays": {"materials": {"Array.materials": ["Material.default", "Material.invisible"]}},
            "geometry": "Geometry.default",
            "materials": [{"*": "Array.materials[query.is_invisible]"}],
            "textures": ["Texture.default"],
            "part_visibility": [{"left_green_eyes": False}],
        },
        f"controller.render.{MODEL}.green_eyes": {
            "arrays": {"materials": {"Array.materials": ["Material.default", "Material.invisible"]}},
            "geometry": "Geometry.default",
            "materials": [{"*": "Array.materials[query.is_invisible]"}],
            "textures": ["Texture.default"],
            "part_visibility": [{"*": False}, {"left_green_eyes": True}],
            "overlay_color": {"r": 0.12, "g": 1, "b": 0.2, "a": 1},
        },
        f"controller.render.{MODEL}.web": {
            "geometry": "Geometry.web",
            "materials": [{"*": "Material.web"}],
            "textures": ["Texture.web"],
            "part_visibility": [{"*": "!query.is_invisible"}],
        },
    },
})
print("Generated paired spider geometry, red/green eyes, seven cobweb panels and sixteen-leg animations.")
