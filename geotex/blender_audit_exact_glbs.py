"""Read-only Blender audit of Draco GLB UV layers and material slots."""

import json
import sys
from pathlib import Path

import bpy


def args():
    values = sys.argv[sys.argv.index("--") + 1:]
    out = Path(values[values.index("--output") + 1])
    glbs = [Path(x) for x in values[values.index("--glb") + 1:values.index("--output")]]
    return glbs, out


def main():
    glbs, out = args()
    records = {}
    for path in glbs:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(path))
        meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        coords = [tuple(obj.matrix_world @ vertex.co) for obj in meshes for vertex in obj.data.vertices]
        bbox_min = [min(c[i] for c in coords) for i in range(3)] if coords else None
        bbox_max = [max(c[i] for c in coords) for i in range(3)] if coords else None
        dims = [(bbox_max[i] - bbox_min[i]) for i in range(3)] if coords else None
        scale = 0.7 / max(dims) if dims and max(dims) > 0 else None
        offset = [-(bbox_min[i] + bbox_max[i]) / 2.0 for i in range(3)] if coords else None
        mesh_records = []
        for obj in meshes:
            data = obj.data
            uv_records = []
            for layer in data.uv_layers:
                values = [tuple(round(float(c), 9) for c in loop.uv) for loop in layer.data]
                uv_records.append({
                    "name": layer.name,
                    "loop_count": len(values),
                    "unique_uv_count": len(set(values)),
                    "uv_min": [min(x[0] for x in values), min(x[1] for x in values)] if values else None,
                    "uv_max": [max(x[0] for x in values), max(x[1] for x in values)] if values else None,
                })
            material_records = []
            for slot in obj.material_slots:
                mat = slot.material
                images = []
                if mat and mat.use_nodes:
                    images = [node.image.name for node in mat.node_tree.nodes if node.type == "TEX_IMAGE" and node.image]
                material_records.append({"name": mat.name if mat else None, "images": images})
            mesh_records.append({"object_name": obj.name, "vertex_count": len(data.vertices), "polygon_count": len(data.polygons), "uv_layers": uv_records, "materials": material_records})
        records[path.stem] = {"path": str(path), "bbox_min": bbox_min, "bbox_max": bbox_max, "historical_normalization": {"scale": scale, "offset": offset, "rule": "scale=0.7/max(world_bbox_dimensions); offset=-bbox_center"}, "mesh_objects": mesh_records}
    out.write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps({"objects": len(records), "output": str(out)}))


if __name__ == "__main__":
    main()
