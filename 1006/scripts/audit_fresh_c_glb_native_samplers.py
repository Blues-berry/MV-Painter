#!/usr/bin/env python3
"""Inventory glTF sampling inputs for the frozen Fresh C 24-object panel."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "1006/data/fresh_c/FRESH_C_GLB_PANEL_SELECTION_20261006.json"
ASSETS = ROOT / "1006/data/fresh_c/assets"
OUT = ROOT / "1006/evidence/audits"
COMPONENT = {5120: "i1", 5121: "u1", 5122: "<i2", 5123: "<u2", 5125: "<u4", 5126: "<f4"}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}
WRAPS = {33071: "CLAMP_TO_EDGE", 33648: "MIRRORED_REPEAT", 10497: "REPEAT"}
FILTERS = {
    9728: "NEAREST", 9729: "LINEAR", 9984: "NEAREST_MIPMAP_NEAREST",
    9985: "LINEAR_MIPMAP_NEAREST", 9986: "NEAREST_MIPMAP_LINEAR",
    9987: "LINEAR_MIPMAP_LINEAR",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_glb(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError(f"invalid GLB v2 header: {path}")
    document, binary = None, b""
    pos = 12
    while pos < len(data):
        size, kind = struct.unpack_from("<I4s", data, pos)
        pos += 8
        chunk = data[pos:pos + size]
        pos += size
        if kind == b"JSON":
            document = json.loads(chunk.decode("utf-8").rstrip("\x00 \t\r\n"))
        elif kind == b"BIN\x00":
            binary = chunk
    if document is None:
        raise ValueError("GLB has no JSON chunk")
    return document, binary


def view_bytes(document: dict, binary: bytes, view_index: int) -> bytes:
    view = document["bufferViews"][view_index]
    if int(view.get("buffer", 0)) != 0:
        raise ValueError("panel GLB references a non-embedded buffer")
    start = int(view.get("byteOffset", 0))
    return binary[start:start + int(view["byteLength"])]


def accessor(document: dict, binary: bytes, index: int) -> np.ndarray:
    spec = document["accessors"][index]
    dtype = np.dtype(COMPONENT[int(spec["componentType"])])
    width = WIDTH[spec["type"]]
    count = int(spec["count"])
    out = np.zeros((count, width), dtype=dtype)
    if "bufferView" in spec:
        view = document["bufferViews"][int(spec["bufferView"])]
        if int(view.get("buffer", 0)) != 0:
            raise ValueError("panel accessor references a non-embedded buffer")
        stride = int(view.get("byteStride", width * dtype.itemsize))
        start = int(view.get("byteOffset", 0)) + int(spec.get("byteOffset", 0))
        out = np.ndarray((count, width), dtype=dtype, buffer=binary, offset=start,
                         strides=(stride, dtype.itemsize)).copy()
    if "sparse" in spec:
        sparse = spec["sparse"]
        idtype = np.dtype(COMPONENT[int(sparse["indices"]["componentType"])])
        ib = view_bytes(document, binary, int(sparse["indices"]["bufferView"]))
        ioff = int(sparse["indices"].get("byteOffset", 0))
        ids = np.frombuffer(ib, dtype=idtype, count=int(sparse["count"]), offset=ioff).astype(int)
        vb = view_bytes(document, binary, int(sparse["values"]["bufferView"]))
        voff = int(sparse["values"].get("byteOffset", 0))
        vals = np.frombuffer(vb, dtype=dtype, count=int(sparse["count"]) * width, offset=voff).reshape(-1, width)
        out[ids] = vals
    if spec.get("normalized"):
        if np.issubdtype(dtype, np.unsignedinteger):
            out = out.astype(np.float64) / np.iinfo(dtype).max
        elif np.issubdtype(dtype, np.signedinteger):
            out = np.maximum(out.astype(np.float64) / np.iinfo(dtype).max, -1.0)
    return out


def image_info(document: dict, binary: bytes, image_index: int, base: Path) -> tuple[str, str, str]:
    spec = document["images"][image_index]
    mime = str(spec.get("mimeType", ""))
    payload = b""
    if "bufferView" in spec:
        payload = view_bytes(document, binary, int(spec["bufferView"]))
    elif str(spec.get("uri", "")).startswith("data:"):
        import base64
        uri = spec["uri"]
        payload = base64.b64decode(uri.split(",", 1)[1])
    elif "uri" in spec:
        image_path = (base.parent / spec["uri"]).resolve()
        payload = image_path.read_bytes()
    if not payload:
        return "", "", mime or "UNRESOLVED"
    with Image.open(io.BytesIO(payload)) as im:
        width, height = im.size
        fmt = im.format or mime or "UNKNOWN"
    return f"{width}x{height}", fmt, mime or fmt


def collect() -> tuple[list[dict], dict]:
    panel = json.loads(PANEL.read_text())
    rows: list[dict] = []
    object_totals = []
    for item in panel["selected"]:
        uid = item["uid"]
        path = ASSETS / f"{uid}.glb"
        digest = sha256(path) if path.exists() else "MISSING"
        doc, binary = read_glb(path)
        materials = doc.get("materials", [])
        textures = doc.get("textures", [])
        samplers = doc.get("samplers", [])
        meshes = doc.get("meshes", [])
        row_count = 0
        uv_n = uv_out_vertices = uv_out_pairs = 0
        object_primitive_n = sum(len(m.get("primitives", [])) for m in meshes)
        object_used_materials = {
            int(prim["material"])
            for mesh in meshes for prim in mesh.get("primitives", [])
            if prim.get("material") is not None
        }
        object_used_textures = set()
        for material_i in object_used_materials:
            binding_i = materials[material_i].get("pbrMetallicRoughness", {}).get("baseColorTexture", {})
            if binding_i.get("index") is not None:
                object_used_textures.add(int(binding_i["index"]))
        used_materials = set()
        used_textures = set()
        for mesh_i, mesh in enumerate(meshes):
            for prim_i, prim in enumerate(mesh.get("primitives", [])):
                attrs = prim.get("attributes", {})
                material_i = prim.get("material")
                mat = materials[int(material_i)] if material_i is not None and int(material_i) < len(materials) else {}
                pbr = mat.get("pbrMetallicRoughness", {})
                binding = pbr.get("baseColorTexture", {})
                texture_i = binding.get("index")
                texcoord_i = int(binding.get("texCoord", 0))
                transform = binding.get("extensions", {}).get("KHR_texture_transform", {})
                if "texCoord" in transform:
                    texcoord_i = int(transform["texCoord"])
                uv_accessor_i = attrs.get(f"TEXCOORD_{texcoord_i}")
                uv = accessor(doc, binary, int(uv_accessor_i)) if uv_accessor_i is not None else np.empty((0, 2))
                finite = np.isfinite(uv).all(axis=1) if len(uv) else np.zeros(0, dtype=bool)
                valid = uv[finite]
                outside_vertex_n = int(np.any((valid < 0.0) | (valid > 1.0), axis=1).sum()) if len(valid) else 0
                outside_pair_n = int(((valid < 0.0) | (valid > 1.0)).sum()) if len(valid) else 0
                uv_n += len(valid)
                uv_out_vertices += outside_vertex_n
                uv_out_pairs += outside_pair_n
                if material_i is not None:
                    used_materials.add(int(material_i))
                texture = textures[int(texture_i)] if texture_i is not None and int(texture_i) < len(textures) else {}
                if texture_i is not None:
                    used_textures.add(int(texture_i))
                sampler_i = texture.get("sampler")
                sampler = samplers[int(sampler_i)] if sampler_i is not None and int(sampler_i) < len(samplers) else {}
                # glTF 2.0 sampler defaults when a property or sampler is omitted.
                wrap_s = int(sampler.get("wrapS", 10497))
                wrap_t = int(sampler.get("wrapT", 10497))
                min_filter = int(sampler.get("minFilter", 9987))
                mag_filter = int(sampler.get("magFilter", 9729))
                source_index = texture.get("source")
                tex_ext = texture.get("extensions", {})
                if source_index is None and "KHR_texture_basisu" in tex_ext:
                    source_index = tex_ext["KHR_texture_basisu"].get("source")
                resolution, image_format, mime = image_info(doc, binary, int(source_index), path) if source_index is not None else ("", "", "UNRESOLVED")
                uv_min = valid.min(axis=0).tolist() if len(valid) else [None, None]
                uv_max = valid.max(axis=0).tolist() if len(valid) else [None, None]
                transform_txt = json.dumps({k: transform[k] for k in ("offset", "rotation", "scale", "texCoord") if k in transform}, separators=(",", ":")) if transform else ""
                row = {
                    "uid": uid, "panel_order": item["panel_order"], "asset_sha256_expected": item["asset_sha256"],
                    "asset_sha256_observed": digest, "asset_hash_match": str(digest == item["asset_sha256"]).upper(),
                    "mesh_index": mesh_i, "primitive_index": prim_i, "primitive_mode": int(prim.get("mode", 4)),
                    "attribute_semantics": "|".join(sorted(attrs)), "material_index": material_i,
                    "material_name": mat.get("name", ""), "baseColorTexture": bool(binding),
                    "texture_index": texture_i, "sampler_index": sampler_i,
                    "wrapS": WRAPS.get(wrap_s, f"UNSUPPORTED_{wrap_s}"), "wrapS_code": wrap_s,
                    "wrapT": WRAPS.get(wrap_t, f"UNSUPPORTED_{wrap_t}"), "wrapT_code": wrap_t,
                    "minFilter": FILTERS.get(min_filter, f"UNSUPPORTED_{min_filter}"), "minFilter_code": min_filter,
                    "magFilter": FILTERS.get(mag_filter, f"UNSUPPORTED_{mag_filter}"), "magFilter_code": mag_filter,
                    "texcoord_set": f"TEXCOORD_{texcoord_i}", "uv_accessor_index": uv_accessor_i,
                    "uv_finite_vertex_n": len(valid), "uv_nonfinite_vertex_n": len(uv) - len(valid),
                    "uv_min_u": uv_min[0], "uv_min_v": uv_min[1], "uv_max_u": uv_max[0], "uv_max_v": uv_max[1],
                    "uv_outside_vertex_fraction": outside_vertex_n / len(valid) if len(valid) else "",
                    "uv_outside_component_fraction": outside_pair_n / (2 * len(valid)) if len(valid) else "",
                    "texture_resolution": resolution, "image_format": image_format, "image_mime_type": mime,
                    "extensions_used": "|".join(doc.get("extensionsUsed", [])),
                    "texture_transform_extension": "KHR_texture_transform" if transform else "",
                    "texture_transform": transform_txt,
                    "alphaMode": mat.get("alphaMode", "OPAQUE"), "alphaCutoff": mat.get("alphaCutoff", 0.5),
                    "doubleSided": mat.get("doubleSided", False),
                    "baseColorFactor": json.dumps(pbr.get("baseColorFactor", [1, 1, 1, 1]), separators=(",", ":")),
                    "primitive_count_object": object_primitive_n,
                    "mesh_count_object": len(meshes), "material_count_object": len(object_used_materials),
                    "material_declaration_count": len(materials), "texture_count_object": len(object_used_textures),
                }
                rows.append(row)
                row_count += 1
        object_totals.append({"uid": uid, "primitive_rows": row_count, "primitive_count": object_primitive_n,
                              "mesh_count": len(meshes), "material_count": len(object_used_materials),
                              "texture_count": len(object_used_textures),
                              "finite_uv_vertices": uv_n, "outside_uv_vertices": uv_out_vertices,
                              "outside_vertex_fraction": uv_out_vertices / uv_n if uv_n else 0.0,
                              "outside_uv_components": uv_out_pairs})
    summary = {
        "panel_id": panel["panel_id"], "frozen_n": panel["selected_n"], "inventory_rows": len(rows),
        "object_n_with_out_of_range_uv": sum(x["outside_uv_vertices"] > 0 for x in object_totals),
        "objects": object_totals,
        "alpha_modes": sorted({r["alphaMode"] for r in rows}),
        "wrapS": sorted({r["wrapS"] for r in rows}), "wrapT": sorted({r["wrapT"] for r in rows}),
        "texture_transform_rows": sum(bool(r["texture_transform_extension"]) for r in rows),
        "nonempty_base_color_texture_rows": sum(r["baseColorTexture"] for r in rows),
        "all_asset_hashes_match": all(r["asset_hash_match"] == "TRUE" for r in rows),
    }
    return rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=OUT / "FRESH_C_GLB_NATIVE_SAMPLER_INVENTORY.csv")
    parser.add_argument("--json", type=Path, default=OUT / "FRESH_C_GLB_NATIVE_SAMPLER_INVENTORY_SUMMARY.json")
    args = parser.parse_args()
    rows, summary = collect()
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    args.json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"csv": str(args.csv), **summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
