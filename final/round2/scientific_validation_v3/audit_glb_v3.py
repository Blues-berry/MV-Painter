#!/usr/bin/env python3
"""Blender GLB audit for the Phase-III bake handoff (Experiment F).

Mirrors final/round2/main_adapter_baking/blender_glb_uv_material_audit.json:
per GLB, world bbox, historical normalization (scale=0.7/max(world dims);
offset=-bbox_center), mesh object names, UV layers, materials. Run inside
Blender 4.2.4 background:
  blender --background --factory-startup --python audit_glb_v3.py --
    --manifest <mvadapter-or-fresh manifest json> --out <out.json>
"""
import argparse
import json
import sys
from mathutils import Vector

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--manifest", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args(argv)

payload = json.load(open(args.manifest))


def audit_one(glb_path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb_path)
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    bpy.context.view_layer.update()

    all_mins, all_maxs = [], []
    for o in meshes:
        for corner in o.bound_box:
            world = o.matrix_world @ Vector(corner)
            all_mins.append(world)
            all_maxs.append(world)
    if not all_mins:
        for o in new:
            bpy.data.objects.remove(o)
        return None
    bbox_min = Vector((min(c.x for c in all_mins), min(c.y for c in all_mins), min(c.z for c in all_mins)))
    bbox_max = Vector((max(c.x for c in all_maxs), max(c.y for c in all_maxs), max(c.z for c in all_maxs)))
    dims = bbox_max - bbox_min
    scale = 0.7 / max(dims)
    offset = -(bbox_min + bbox_max) / 2

    mesh_records = []
    for o in meshes:
        uv_layers = []
        for ul in o.data.uv_layers:
            uvs = [tuple(d.uv) for d in ul.data]
            unique = {tuple(round(c, 9) for c in uv) for uv in uvs}
            uv_layers.append({
                "name": ul.name,
                "loop_count": len(uvs),
                "unique_uv_count": len(unique),
                "uv_min": [min(u[0] for u in uvs), min(u[1] for u in uvs)],
                "uv_max": [max(u[0] for u in uvs), max(u[1] for u in uvs)],
            })
        materials = []
        for slot in o.material_slots:
            if slot.material is None:
                continue
            images = []
            if slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image:
                        images.append(node.image.name)
            materials.append({"name": slot.material.name, "images": images})
        mesh_records.append({
            "object_name": o.name,
            "vertex_count": len(o.data.vertices),
            "polygon_count": len(o.data.polygons),
            "uv_layers": uv_layers,
            "materials": materials,
        })
    for o in new:
        bpy.data.objects.remove(o)
    return {
        "bbox_min": list(bbox_min),
        "bbox_max": list(bbox_max),
        "historical_normalization": {
            "scale": scale,
            "offset": [offset.x, offset.y, offset.z],
            "rule": "scale=0.7/max(world_bbox_dimensions); offset=-bbox_center",
        },
        "mesh_objects": mesh_records,
    }


out = {}
for row in payload["objects"]:
    uid = row["source_uid"]
    rec = audit_one(row["mesh_path"])
    if rec is not None:
        out[uid] = rec
        out[uid]["path"] = row["mesh_path"]
        print(f"audited {uid}: {len(rec['mesh_objects'])} meshes", flush=True)

json.dump(out, open(args.out, "w"), indent=2)
print("wrote", args.out, len(out))
