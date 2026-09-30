"""Minimal CPU texture baking and software unseen-view validation.

The script is executed by Blender 4.2 in background mode. Blender is used for
the authoritative glTF import/export and material binding; the projection,
z-buffer visibility, UV splatting, and unseen-view rasterization are explicit
NumPy CPU operations. No proxy mesh, re-unwrap, or CUDA rasterizer is used.

Example::

    blender --background --factory-startup --python geotex/cpu_texture_bake.py -- \
      --handoff final/round2/main_adapter_baking/BAKE_INPUT_HANDOFF.json \
      --output-dir final/round2/main_adapter_baking/cpu_bake_smoke \
      --objects obj_0015,obj_0013 \
      --methods gt,no_adapter,fixed_low,fixed_high,c3
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

try:
    import bpy
except ImportError as exc:  # pragma: no cover - exercised only inside Blender
    raise RuntimeError("cpu_texture_bake.py must run inside Blender background Python") from exc


METHODS = ("gt", "no_adapter", "fixed_low", "fixed_high", "c3")
UNSEEN = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--objects", required=True, help="comma-separated object IDs")
    parser.add_argument("--methods", default=",".join(METHODS))
    parser.add_argument("--texture-resolution", type=int, default=1024)
    parser.add_argument("--render-resolution", type=int, default=512)
    parser.add_argument("--inpaint-iterations", type=int, default=8, help="explicit UV-neighbor fill iterations; 0 disables it")
    parser.add_argument("--max-triangles", type=int, default=0, help="debug guard; 0 means no limit")
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def load_scene(path: Path) -> None:
    clear_scene()
    result = bpy.ops.import_scene.gltf(filepath=str(path))
    if "FINISHED" not in result:
        raise RuntimeError(f"glTF import failed for {path}: {result}")


def load_rgba(path: Path) -> np.ndarray:
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        width, height = image.size
        if width <= 0 or height <= 0:
            raise ValueError(f"invalid image dimensions for {path}: {image.size[:]}")
        # Blender's Image.pixels is bottom-up; return conventional top-down H,W,C.
        raw = np.asarray(image.pixels[:], dtype=np.float32).reshape(height, width, 4)
        return np.flip(raw, axis=0).copy()
    finally:
        bpy.data.images.remove(image)


def save_rgba(path: Path, rgba_top_down: np.ndarray) -> None:
    rgba = np.asarray(rgba_top_down, dtype=np.float32).clip(0.0, 1.0)
    if rgba.ndim != 3 or rgba.shape[-1] != 4:
        raise ValueError(f"expected H,W,4 image, got {rgba.shape}")
    path.parent.mkdir(parents=True, exist_ok=True)
    height, width = rgba.shape[:2]
    image = bpy.data.images.new(path.stem, width=width, height=height, alpha=True, float_buffer=False)
    try:
        image.colorspace_settings.name = "sRGB"
        image.pixels.foreach_set(np.flip(rgba, axis=0).reshape(-1).tolist())
        image.filepath_raw = str(path)
        image.file_format = "PNG"
        image.save()
    finally:
        bpy.data.images.remove(image)


def save_rgb(path: Path, rgb_top_down: np.ndarray) -> None:
    rgb = np.asarray(rgb_top_down, dtype=np.float32).clip(0.0, 1.0)
    alpha = np.ones((*rgb.shape[:2], 1), dtype=np.float32)
    save_rgba(path, np.concatenate([rgb, alpha], axis=-1))


def object_records(handoff: dict, requested: list[str]) -> list[dict]:
    by_id = {record["object"]: record for record in handoff["objects"]}
    missing = [object_id for object_id in requested if object_id not in by_id]
    if missing:
        raise KeyError(f"objects not in handoff: {missing}")
    return [by_id[object_id] for object_id in requested]


def imported_mesh_objects(audit_record: dict | None = None) -> list:
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if audit_record is None:
        return mesh_objects
    expected = {item["object_name"] for item in audit_record["mesh_material_audit"]}
    selected = [obj for obj in mesh_objects if obj.name in expected]
    if len(selected) != len(expected):
        raise RuntimeError(
            f"mesh audit mismatch for {audit_record['object']}: expected {sorted(expected)}, "
            f"found {[obj.name for obj in selected]}"
        )
    return selected


def extract_geometry(audit_record: dict | None = None, max_triangles: int = 0) -> dict:
    """Extract original mesh triangles and UVs without changing the Blender mesh."""
    meshes = imported_mesh_objects(audit_record)
    triangles = []
    triangle_uvs = []
    seam_edges: dict[tuple[int, int], list[tuple[np.ndarray, np.ndarray]]] = {}
    vertex_offset = 0
    for obj in meshes:
        mesh = obj.data
        mesh.calc_loop_triangles()
        uv_layer = mesh.uv_layers.get("UVMap") or mesh.uv_layers.active
        if uv_layer is None:
            raise RuntimeError(f"mesh {obj.name} has no UV layer")
        matrix = np.asarray(obj.matrix_world, dtype=np.float64)
        local_vertices = np.asarray([tuple(vertex.co) for vertex in mesh.vertices], dtype=np.float64)
        world_vertices = (local_vertices @ matrix[:3, :3].T) + matrix[:3, 3]

        # Use polygon loops to identify UV discontinuities on shared geometric edges.
        for polygon in mesh.polygons:
            loops = list(polygon.loop_indices)
            for index, loop_index in enumerate(loops):
                next_loop = loops[(index + 1) % len(loops)]
                va = mesh.loops[loop_index].vertex_index
                vb = mesh.loops[next_loop].vertex_index
                key = (min(va, vb) + vertex_offset, max(va, vb) + vertex_offset)
                seam_edges.setdefault(key, []).append(
                    (
                        np.asarray(uv_layer.data[loop_index].uv[:], dtype=np.float64),
                        np.asarray(uv_layer.data[next_loop].uv[:], dtype=np.float64),
                    )
                )

        for loop_triangle in mesh.loop_triangles:
            vertices = [world_vertices[index] for index in loop_triangle.vertices]
            uvs = [np.asarray(uv_layer.data[index].uv[:], dtype=np.float64) for index in loop_triangle.loops]
            triangles.append(vertices)
            triangle_uvs.append(uvs)
            if max_triangles and len(triangles) >= max_triangles:
                break
        vertex_offset += len(mesh.vertices)
        if max_triangles and len(triangles) >= max_triangles:
            break

    if not triangles:
        raise RuntimeError("no mesh triangles extracted")
    seam_pairs = []
    for entries in seam_edges.values():
        if len(entries) < 2:
            continue
        first = entries[0]
        for other in entries[1:]:
            if np.linalg.norm(first[0] - other[0]) + np.linalg.norm(first[1] - other[1]) > 1e-5:
                seam_pairs.append((0.5 * (first[0] + first[1]), 0.5 * (other[0] + other[1])))

    return {
        "triangles": np.asarray(triangles, dtype=np.float32),
        "triangle_uvs": np.asarray(triangle_uvs, dtype=np.float32),
        "seam_pairs": np.asarray(seam_pairs, dtype=np.float32).reshape(-1, 2, 2),
        "mesh_object_count": len(meshes),
        "triangle_count": len(triangles),
    }


def normalize_geometry(geometry: dict, record: dict) -> dict:
    geometry = dict(geometry)
    geometry["triangles"] = float(record["normalization"]["scale"]) * (
        geometry["triangles"] + np.asarray(record["normalization"]["offset"], dtype=np.float32)
    )
    return geometry


def project_triangles(triangles: np.ndarray, camera: dict, width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
    extrinsic = np.asarray(camera["extrinsic"], dtype=np.float32)
    # The handoff stores the historical Blender/OpenCV world-to-camera pose:
    # camera x/y are already image-right/image-down and z is forward.
    rotation = extrinsic[:, :3]
    translation = extrinsic[:, 3]
    camera_points = triangles @ rotation.T + translation
    if str(camera.get("camera", "ortho")).lower().startswith("ortho"):
        # The project camera convention uses a unit orthographic square.
        x = (camera_points[:, :, 0] + 0.5) * width
        y = (0.5 + camera_points[:, :, 1]) * height
    else:
        intrinsic = np.asarray(camera["intrinsic"], dtype=np.float32)
        z = np.maximum(camera_points[:, :, 2], 1e-8)
        x = intrinsic[0, 0] * camera_points[:, :, 0] / z + intrinsic[0, 2]
        y = intrinsic[1, 1] * camera_points[:, :, 1] / z + intrinsic[1, 2]
    return np.stack([x, y], axis=-1), camera_points[:, :, 2]


def rasterize(geometry: dict, camera: dict, width: int, height: int) -> dict:
    """CPU triangle z-buffer with barycentric coordinates at visible pixels."""
    screen, depths = project_triangles(geometry["triangles"], camera, width, height)
    z_buffer = np.full((height, width), np.inf, dtype=np.float32)
    triangle_buffer = np.full((height, width), -1, dtype=np.int32)
    bary_buffer = np.zeros((height, width, 3), dtype=np.float32)
    triangle_count = len(screen)

    for index in range(triangle_count):
        p0, p1, p2 = screen[index]
        x_min = max(0, int(math.floor(float(np.min(screen[index, :, 0]) - 0.5))))
        x_max = min(width - 1, int(math.ceil(float(np.max(screen[index, :, 0]) - 0.5))))
        y_min = max(0, int(math.floor(float(np.min(screen[index, :, 1]) - 0.5))))
        y_max = min(height - 1, int(math.ceil(float(np.max(screen[index, :, 1]) - 0.5))))
        if x_min > x_max or y_min > y_max:
            continue
        denominator = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if abs(float(denominator)) < 1e-10:
            continue
        xs = np.arange(x_min, x_max + 1, dtype=np.float32) + 0.5
        ys = np.arange(y_min, y_max + 1, dtype=np.float32) + 0.5
        grid_x, grid_y = np.meshgrid(xs, ys)
        weight0 = ((p1[1] - p2[1]) * (grid_x - p2[0]) + (p2[0] - p1[0]) * (grid_y - p2[1])) / denominator
        weight1 = ((p2[1] - p0[1]) * (grid_x - p2[0]) + (p0[0] - p2[0]) * (grid_y - p2[1])) / denominator
        weight2 = 1.0 - weight0 - weight1
        inside = (weight0 >= -1e-5) & (weight1 >= -1e-5) & (weight2 >= -1e-5)
        if not np.any(inside):
            continue
        local_depth = weight0 * depths[index, 0] + weight1 * depths[index, 1] + weight2 * depths[index, 2]
        current = z_buffer[y_min : y_max + 1, x_min : x_max + 1]
        closer = inside & (local_depth < current)
        if not np.any(closer):
            continue
        current[closer] = local_depth[closer]
        triangle_buffer[y_min : y_max + 1, x_min : x_max + 1][closer] = index
        local_bary = bary_buffer[y_min : y_max + 1, x_min : x_max + 1]
        local_bary[closer, 0] = weight0[closer]
        local_bary[closer, 1] = weight1[closer]
        local_bary[closer, 2] = weight2[closer]

    return {"triangle": triangle_buffer, "bary": bary_buffer, "depth": z_buffer}


def image_for_record(record: dict, method: str, slot: int, raw_view: int, rotated: bool) -> tuple[np.ndarray, np.ndarray]:
    if method == "gt":
        rgba = load_rgba(Path(record["gt_rgba_17"][raw_view]))
        return rgba[:, :, :3] * rgba[:, :, 3:4] + (1.0 - rgba[:, :, 3:4]), rgba[:, :, 3]
    path = Path(record["generated_conditions"][method]["target_views"][slot]["path"])
    rgb = load_rgba(path)[:, :, :3]
    source_mask = load_rgba(Path(record["foreground_masks_17"][raw_view]))[:, :, 0]
    if source_mask.shape != rgb.shape[:2]:
        y_index = np.minimum((np.arange(rgb.shape[0]) * source_mask.shape[0] / rgb.shape[0]).astype(np.int32), source_mask.shape[0] - 1)
        x_index = np.minimum((np.arange(rgb.shape[1]) * source_mask.shape[1] / rgb.shape[1]).astype(np.int32), source_mask.shape[1] - 1)
        source_mask = source_mask[y_index][:, x_index]
    if rotated:
        # Dataset rotation is +90° CCW; undo it before using the raw camera.
        rgb = np.rot90(rgb, k=3).copy()
        source_mask = np.rot90(source_mask, k=3).copy()
    return rgb, source_mask


def splat_view(
    texture_sum: np.ndarray,
    texture_weight: np.ndarray,
    view_sum: np.ndarray,
    view_weight: np.ndarray,
    geometry: dict,
    raster: dict,
    image: np.ndarray,
    source_mask: np.ndarray,
    texture_resolution: int,
) -> None:
    valid = (raster["triangle"] >= 0) & (source_mask > 0.5)
    if not np.any(valid):
        return
    triangle_ids = raster["triangle"][valid]
    bary = raster["bary"][valid]
    uvs = (geometry["triangle_uvs"][triangle_ids] * bary[:, :, None]).sum(axis=1)
    colors = image[np.where(valid)]
    coordinate_x = np.clip(uvs[:, 0], 0.0, 1.0) * (texture_resolution - 1)
    coordinate_y = np.clip(1.0 - uvs[:, 1], 0.0, 1.0) * (texture_resolution - 1)
    x0 = np.floor(coordinate_x).astype(np.int32)
    y0 = np.floor(coordinate_y).astype(np.int32)
    x1 = np.minimum(x0 + 1, texture_resolution - 1)
    y1 = np.minimum(y0 + 1, texture_resolution - 1)
    fx = coordinate_x - x0
    fy = coordinate_y - y0
    for xx, yy, weight in ((x0, y0, (1.0 - fx) * (1.0 - fy)), (x1, y0, fx * (1.0 - fy)), (x0, y1, (1.0 - fx) * fy), (x1, y1, fx * fy)):
        np.add.at(texture_sum, (yy, xx), colors * weight[:, None])
        np.add.at(texture_weight, (yy, xx), weight)
        np.add.at(view_sum, (yy, xx), colors * weight[:, None])
        np.add.at(view_weight, (yy, xx), weight)


def seam_discontinuity(texture: np.ndarray, seam_pairs: np.ndarray) -> float:
    if len(seam_pairs) == 0:
        return float("nan")
    size = texture.shape[0]
    values = []
    for first, second in seam_pairs:
        points = []
        for uv in (first, second):
            x = int(round(float(np.clip(uv[0], 0.0, 1.0) * (size - 1))))
            y = int(round(float(np.clip(1.0 - uv[1], 0.0, 1.0) * (size - 1))))
            points.append(texture[y, x])
        values.append(float(np.linalg.norm(points[0] - points[1])))
    return float(np.mean(values))


def explicit_uv_inpaint(texture: np.ndarray, coverage: np.ndarray, iterations: int) -> tuple[np.ndarray, np.ndarray]:
    """Fill only small UV holes by explicit 4-neighbor propagation.

    The original coverage mask is never discarded. The returned mask records
    which texels became usable after the explicitly requested fill.
    """
    filled = np.asarray(coverage, dtype=bool).copy()
    result = np.asarray(texture, dtype=np.float32).copy()
    for _ in range(max(0, iterations)):
        total = np.zeros_like(result)
        count = np.zeros(filled.shape, dtype=np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            source = np.zeros_like(result)
            source_mask = np.zeros_like(filled)
            y0, y1 = max(0, dy), min(filled.shape[0], filled.shape[0] + dy)
            x0, x1 = max(0, dx), min(filled.shape[1], filled.shape[1] + dx)
            sy0, sy1 = max(0, -dy), min(filled.shape[0], filled.shape[0] - dy)
            sx0, sx1 = max(0, -dx), min(filled.shape[1], filled.shape[1] - dx)
            source[y0:y1, x0:x1] = result[sy0:sy1, sx0:sx1]
            source_mask[y0:y1, x0:x1] = filled[sy0:sy1, sx0:sx1]
            total[source_mask] += source[source_mask]
            count[source_mask] += 1.0
        update = (~filled) & (count > 0)
        if not np.any(update):
            break
        result[update] = total[update] / count[update, None]
        filled[update] = True
    return result.clip(0.0, 1.0), filled


def bake_texture(record: dict, geometry: dict, method: str, args: argparse.Namespace, raster_cache: dict) -> dict:
    size = args.texture_resolution
    texture_sum = np.zeros((size, size, 3), dtype=np.float32)
    texture_weight = np.zeros((size, size), dtype=np.float32)
    sum_views = np.zeros((size, size, 3), dtype=np.float32)
    sum_square_views = np.zeros((size, size, 3), dtype=np.float32)
    count_views = np.zeros((size, size), dtype=np.int32)
    mapping = record["target_view_mapping"]
    for slot, item in enumerate(mapping):
        raw_view = int(item["raw_view_index"])
        image, source_mask = image_for_record(record, method, slot, raw_view, bool(item["rotated_ccw_90"]))
        height, width = image.shape[:2]
        cache_key = (raw_view, width, height)
        if cache_key not in raster_cache:
            camera = record["camera_poses_17"][raw_view]
            raster_cache[cache_key] = rasterize(geometry, camera, width, height)
        raster = raster_cache[cache_key]
        view_sum = np.zeros((size, size, 3), dtype=np.float32)
        view_weight = np.zeros((size, size), dtype=np.float32)
        splat_view(texture_sum, texture_weight, view_sum, view_weight, geometry, raster, image, source_mask, size)
        hit = view_weight > 1e-8
        if np.any(hit):
            average = np.zeros_like(view_sum)
            average[hit] = view_sum[hit] / view_weight[hit, None]
            sum_views[hit] += average[hit]
            sum_square_views[hit] += average[hit] * average[hit]
            count_views[hit] += 1

    covered = texture_weight > 1e-8
    raw_texture = np.ones((size, size, 3), dtype=np.float32)
    raw_texture[covered] = texture_sum[covered] / texture_weight[covered, None]
    raw_texture = raw_texture.clip(0.0, 1.0)
    texture, inpainted = explicit_uv_inpaint(raw_texture, covered, args.inpaint_iterations)
    valid_multi = count_views > 1
    cross_view_variance = float("nan")
    if np.any(valid_multi):
        mean = sum_views[valid_multi] / count_views[valid_multi, None]
        second = sum_square_views[valid_multi] / count_views[valid_multi, None]
        cross_view_variance = float(np.maximum(second - mean * mean, 0.0).mean())
    return {
        "texture": texture,
        "raw_texture": raw_texture,
        "coverage": covered,
        "inpainted_coverage": inpainted,
        "texture_coverage": float(covered.mean()),
        "texture_coverage_after_inpaint": float(inpainted.mean()),
        "inpainted_fraction": float((inpainted & ~covered).mean()),
        "cross_view_texel_variance": cross_view_variance,
        "uv_seam_discontinuity": seam_discontinuity(texture, geometry["seam_pairs"]),
        "source_view_count": len(mapping),
        "blend": "uniform visible-pixel UV bilinear splat; optional explicit 4-neighbor UV inpainting",
    }


def create_textured_materials(texture: np.ndarray, texture_path: Path, mesh_objects: list) -> object:
    save_rgb(texture_path, texture)
    image = bpy.data.images.load(str(texture_path), check_existing=False)
    image.colorspace_settings.name = "sRGB"
    image.pack()
    material = bpy.data.materials.new(f"CPU_Baked_{texture_path.stem}")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    texture_node = nodes.new("ShaderNodeTexImage")
    texture_node.image = image
    shader.inputs["Roughness"].default_value = 0.8
    links.new(texture_node.outputs["Color"], shader.inputs["Base Color"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    for obj in mesh_objects:
        obj.data.materials.clear()
        obj.data.materials.append(material)
        for polygon in obj.data.polygons:
            polygon.material_index = 0
    return material


def export_selected_glb(path: Path, mesh_objects: list) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objects[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    result = bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_materials="EXPORT",
        export_texcoords=True,
        export_normals=True,
    )
    if "FINISHED" not in result or not path.is_file():
        raise RuntimeError(f"textured GLB export failed: {path} ({result})")


def find_material_image(obj) -> object:
    for material in obj.data.materials:
        if material is None or not material.use_nodes:
            continue
        for node in material.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image is not None:
                return node.image
    return None


def verify_export_and_extract(path: Path, record: dict, max_triangles: int) -> tuple[dict, np.ndarray]:
    load_scene(path)
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError(f"exported GLB contains no mesh objects: {path}")
    images = [find_material_image(obj) for obj in mesh_objects]
    if any(image is None for image in images):
        raise RuntimeError(f"exported GLB has a mesh without an image texture: {path}")
    first = images[0]
    width, height = first.size
    raw = np.asarray(first.pixels[:], dtype=np.float32).reshape(height, width, 4)
    texture = np.flip(raw[:, :, :3], axis=0).copy()
    for image in images[1:]:
        if tuple(image.size) != (width, height):
            raise RuntimeError("exported GLB mesh materials use inconsistent texture sizes")
    geometry = extract_geometry(None, max_triangles=max_triangles)
    return normalize_geometry(geometry, record), texture


def render_textured_view(geometry: dict, texture: np.ndarray, camera: dict, resolution: int, cache: dict) -> tuple[np.ndarray, np.ndarray]:
    key = (id(geometry["triangles"]), int(camera["azimuth"]), int(camera["elevation"]), resolution)
    if key not in cache:
        cache[key] = rasterize(geometry, camera, resolution, resolution)
    raster = cache[key]
    output = np.ones((resolution, resolution, 3), dtype=np.float32)
    alpha = (raster["triangle"] >= 0).astype(np.float32)
    valid = alpha > 0.5
    if np.any(valid):
        triangle_ids = raster["triangle"][valid]
        bary = raster["bary"][valid]
        uv = (geometry["triangle_uvs"][triangle_ids] * bary[:, :, None]).sum(axis=1)
        size = texture.shape[0]
        x = np.clip(uv[:, 0], 0.0, 1.0) * (size - 1)
        y = np.clip(1.0 - uv[:, 1], 0.0, 1.0) * (size - 1)
        x0 = np.floor(x).astype(np.int32)
        y0 = np.floor(y).astype(np.int32)
        x1 = np.minimum(x0 + 1, size - 1)
        y1 = np.minimum(y0 + 1, size - 1)
        fx = x - x0
        fy = y - y0
        colors = (
            texture[y0, x0] * ((1 - fx) * (1 - fy))[:, None]
            + texture[y0, x1] * (fx * (1 - fy))[:, None]
            + texture[y1, x0] * ((1 - fx) * fy)[:, None]
            + texture[y1, x1] * (fx * fy)[:, None]
        )
        output[valid] = colors
    return output.clip(0.0, 1.0), alpha


def bake_one(
    record: dict,
    method: str,
    args: argparse.Namespace,
    prepared_geometry: dict | None = None,
    prepared_source_rasters: dict | None = None,
    render_state: dict | None = None,
) -> dict:
    object_id = record["object"]
    input_glb = Path(record["exact_glb_path"])
    load_scene(input_glb)
    source_geometry = prepared_geometry or normalize_geometry(extract_geometry(record, args.max_triangles), record)
    mesh_objects = imported_mesh_objects(record)
    raster_cache = prepared_source_rasters if prepared_source_rasters is not None else {}
    baked = bake_texture(record, source_geometry, method, args, raster_cache)
    method_dir = args.output_dir / method / object_id
    method_dir.mkdir(parents=True, exist_ok=True)
    texture_path = method_dir / f"{object_id}_{method}_texture.png"
    coverage_path = method_dir / f"{object_id}_{method}_coverage.png"
    save_rgb(texture_path, baked["texture"])
    save_rgba(coverage_path, np.dstack([baked["coverage"].astype(np.float32)] * 3 + [np.ones_like(baked["coverage"], dtype=np.float32)]))
    save_rgba(method_dir / f"{object_id}_{method}_inpainted_coverage.png", np.dstack([baked["inpainted_coverage"].astype(np.float32)] * 3 + [np.ones_like(baked["inpainted_coverage"], dtype=np.float32)]))
    material = create_textured_materials(baked["texture"], texture_path, mesh_objects)
    material_name = material.name
    exported_glb = method_dir / f"{object_id}_{method}_textured.glb"
    export_selected_glb(exported_glb, mesh_objects)
    exported_geometry, exported_texture = verify_export_and_extract(exported_glb, record, args.max_triangles)
    if render_state is not None:
        if render_state.get("geometry") is None:
            render_state["geometry"] = exported_geometry
        else:
            cached_geometry = render_state["geometry"]
            if not np.array_equal(cached_geometry["triangles"], exported_geometry["triangles"]) or not np.array_equal(cached_geometry["triangle_uvs"], exported_geometry["triangle_uvs"]):
                raise RuntimeError("exported GLB geometry/UV changed between bake methods")
        render_geometry = render_state["geometry"]
        render_cache = render_state.setdefault("raster_cache", {})
    else:
        render_geometry = exported_geometry
        render_cache = {}
    render_dir = method_dir / "unseen_renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    for raw_view in UNSEEN:
        rgb, alpha = render_textured_view(
            render_geometry,
            exported_texture,
            record["camera_poses_17"][raw_view],
            args.render_resolution,
            render_cache,
        )
        save_rgba(render_dir / f"view_{raw_view:03d}.png", np.dstack([rgb, alpha]))
    metadata = {
        "object": object_id,
        "method": method,
        "input_exact_glb": str(input_glb),
        "output_textured_glb": str(exported_glb),
        "texture_path": str(texture_path),
        "coverage_path": str(coverage_path),
        "unseen_render_dir": str(render_dir),
        "mesh_object_count": source_geometry["mesh_object_count"],
        "triangle_count": source_geometry["triangle_count"],
        "texture_resolution": args.texture_resolution,
        "render_resolution": args.render_resolution,
        "source_views": [int(item["raw_view_index"]) for item in record["target_view_mapping"]],
        "unseen_views": list(UNSEEN),
        "texture_coverage": baked["texture_coverage"],
        "texture_coverage_after_inpaint": baked["texture_coverage_after_inpaint"],
        "inpainted_fraction": baked["inpainted_fraction"],
        "cross_view_texel_variance": baked["cross_view_texel_variance"],
        "uv_seam_discontinuity": baked["uv_seam_discontinuity"],
        "inpainting": {
            "iterations": args.inpaint_iterations,
            "rule": "explicit 4-neighbor UV propagation",
            "raw_coverage_preserved": True,
            "inpainted_fraction": baked["inpainted_fraction"],
        },
        "blend": baked["blend"],
        "exported_glb_image_texture_verified": True,
        "material_name": material_name,
    }
    (method_dir / "bake_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main() -> None:
    args = parse_args()
    args.handoff = args.handoff.resolve()
    args.output_dir = args.output_dir.resolve()
    handoff = json.loads(args.handoff.read_text())
    requested_objects = [value.strip() for value in args.objects.split(",") if value.strip()]
    requested_methods = [value.strip() for value in args.methods.split(",") if value.strip()]
    records = object_records(handoff, requested_objects)
    # Allow any method whose per-view inputs exist in the handoff record
    # (extension point for layer-wise conditions); keep the classic names too.
    handoff_conditions = set()
    for record in records:
        handoff_conditions.update(record.get("generated_conditions", {}).keys())
    invalid_methods = [
        method for method in requested_methods
        if method not in set(METHODS) | handoff_conditions
    ]
    if invalid_methods:
        raise ValueError(
            f"unsupported methods: {invalid_methods}; choose from {sorted(set(METHODS) | handoff_conditions)}"
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_metadata = []
    for record in records:
        # Visibility depends only on the frozen geometry, cameras, and image
        # resolution. Prepare it once per object and reuse it across GT and
        # all four generated conditions.
        load_scene(Path(record["exact_glb_path"]))
        prepared_geometry = normalize_geometry(extract_geometry(record, args.max_triangles), record)
        prepared_source_rasters = {}
        source_resolutions = {(256, 256)}
        if "gt" in requested_methods:
            source_resolutions.add((512, 512))
        for item in record["target_view_mapping"]:
            raw_view = int(item["raw_view_index"])
            camera = record["camera_poses_17"][raw_view]
            for width, height in sorted(source_resolutions):
                prepared_source_rasters[(raw_view, width, height)] = rasterize(
                    prepared_geometry, camera, width, height
                )
        render_state = {"geometry": None, "raster_cache": {}}
        for method in requested_methods:
            print(f"[CPU-BAKE] {record['object']} {method}", flush=True)
            all_metadata.append(
                bake_one(
                    record,
                    method,
                    args,
                    prepared_geometry=prepared_geometry,
                    prepared_source_rasters=prepared_source_rasters,
                    render_state=render_state,
                )
            )
    summary = {
        "protocol": "codex-d-cpu-texture-bake-v1",
        "handoff": str(args.handoff),
        "objects": requested_objects,
        "methods": requested_methods,
        "texture_resolution": args.texture_resolution,
        "render_resolution": args.render_resolution,
        "implementation": "Blender glTF import/export + NumPy CPU z-buffer/UV bilinear splat/rasterizer",
        "records": all_metadata,
    }
    (args.output_dir / "BAKE_RUN_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"objects": len(records), "methods": requested_methods, "records": len(all_metadata), "output_dir": str(args.output_dir)}, indent=2))


if __name__ == "__main__":
    main()
