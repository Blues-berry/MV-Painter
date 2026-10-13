"""Append a baked PNG to a GLB without re-exporting or modifying its mesh."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import struct
from pathlib import Path

from PIL import Image


GLB_MAGIC = b"glTF"
JSON_CHUNK = b"JSON"
BIN_CHUNK = b"BIN\x00"
GLB_VERSION = 2
REPEAT = 10497


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_glb(path: Path) -> tuple[dict, list[tuple[bytes, bytes]]]:
    data = path.read_bytes()
    if len(data) < 12:
        raise ValueError(f"truncated GLB header: {path}")
    magic, version, declared_length = struct.unpack_from("<4sII", data)
    if magic != GLB_MAGIC or version != GLB_VERSION or declared_length != len(data):
        raise ValueError(f"invalid GLB v2 header: {path}")
    chunks = []
    cursor = 12
    document = None
    while cursor < len(data):
        if cursor + 8 > len(data):
            raise ValueError("truncated GLB chunk header")
        length, kind = struct.unpack_from("<I4s", data, cursor)
        cursor += 8
        payload = data[cursor:cursor + length]
        if len(payload) != length:
            raise ValueError("truncated GLB chunk")
        cursor += length
        chunks.append((kind, payload))
        if kind == JSON_CHUNK:
            document = json.loads(payload.decode("utf-8").rstrip("\x00 \t\r\n"))
    if document is None:
        raise ValueError(f"GLB has no JSON chunk: {path}")
    return document, chunks


def serialize_glb(document: dict, chunks: list[tuple[bytes, bytes]]) -> bytes:
    json_payload = json.dumps(document, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    json_payload += b" " * ((-len(json_payload)) % 4)
    normalized = []
    for kind, payload in chunks:
        if kind == JSON_CHUNK:
            payload = json_payload
        if len(payload) % 4:
            payload += b"\x00" * ((-len(payload)) % 4)
        normalized.append((kind, payload))
    total = 12 + sum(8 + len(payload) for _, payload in normalized)
    output = bytearray(struct.pack("<4sII", GLB_MAGIC, GLB_VERSION, total))
    for kind, payload in normalized:
        output.extend(struct.pack("<I4s", len(payload), kind))
        output.extend(payload)
    return bytes(output)


def source_sampler(document: dict, material_index: int) -> tuple[dict, int | None, int | None]:
    materials = document.get("materials", [])
    if not 0 <= material_index < len(materials):
        raise IndexError(f"material index {material_index} is out of range")
    info = materials[material_index].get("pbrMetallicRoughness", {}).get("baseColorTexture")
    if not info:
        return {}, None, None
    texture_index = int(info["index"])
    texture = document.get("textures", [])[texture_index]
    sampler_index = texture.get("sampler")
    sampler = document.get("samplers", [])[int(sampler_index)] if sampler_index is not None else {}
    return sampler, texture_index, int(sampler_index) if sampler_index is not None else None


def patch_basecolor_texture(
    source_path: Path,
    texture_path: Path,
    output_path: Path,
    material_index: int = 0,
    texture_name: str | None = None,
    expected_resolution: int = 1024,
) -> dict:
    source_hash_before = sha256_file(source_path)
    source_document, source_chunks = read_glb(source_path)
    document = copy.deepcopy(source_document)
    source_bin = next((payload for kind, payload in source_chunks if kind == BIN_CHUNK), None)
    if source_bin is None or not document.get("buffers"):
        raise ValueError("source GLB must contain an embedded binary buffer")
    if len(document["buffers"]) != 1 or int(document["buffers"][0].get("buffer", 0)) != 0:
        raise ValueError("only the single embedded GLB buffer is supported")
    if document["buffers"][0].get("uri"):
        raise ValueError("GLB buffer unexpectedly uses an external URI")
    with Image.open(texture_path) as image:
        if image.size != (expected_resolution, expected_resolution):
            raise ValueError(f"expected {expected_resolution}x{expected_resolution} texture, got {image.size}")
        image.load()
    png_bytes = texture_path.read_bytes()
    old_materials = copy.deepcopy(source_document.get("materials", []))
    old_texture_count = len(source_document.get("textures", []))
    old_image_count = len(source_document.get("images", []))
    old_view_count = len(source_document.get("bufferViews", []))
    old_sampler, original_texture_index, sampler_index = source_sampler(source_document, material_index)

    images = document.setdefault("images", [])
    textures = document.setdefault("textures", [])
    views = document.setdefault("bufferViews", [])
    samplers = document.setdefault("samplers", [])
    buffer = document["buffers"][0]
    # Preserve the complete original BIN chunk, including its at-most-three
    # padding bytes, so all prior binary accessors remain byte-identical.
    image_offset = len(source_bin)
    if image_offset % 4:
        raise ValueError("GLB BIN chunk is not 4-byte aligned")
    image_index = len(images)
    view_index = len(views)
    texture_index = len(textures)
    views.append({"buffer": 0, "byteOffset": image_offset, "byteLength": len(png_bytes)})
    images.append({"name": texture_name or texture_path.stem, "bufferView": view_index, "mimeType": "image/png"})

    texture_spec = {"source": image_index}
    if sampler_index is not None:
        texture_spec["sampler"] = sampler_index
    elif original_texture_index is not None:
        # Preserve the source texture's implicit glTF defaults.
        pass
    else:
        sampler_index = len(samplers)
        samplers.append({"wrapS": REPEAT, "wrapT": REPEAT, "magFilter": 9729, "minFilter": 9987})
        texture_spec["sampler"] = sampler_index
    textures.append(texture_spec)

    pbr = document["materials"][material_index].setdefault("pbrMetallicRoughness", {})
    if original_texture_index is None:
        pbr["baseColorTexture"] = {"index": texture_index, "texCoord": 0}
    else:
        base_info = pbr["baseColorTexture"]
        base_info["index"] = texture_index
    buffer["byteLength"] = image_offset + len(png_bytes)

    replaced_chunks = []
    for kind, payload in source_chunks:
        if kind == JSON_CHUNK:
            replaced_chunks.append((kind, b""))
        elif kind == BIN_CHUNK:
            replaced_chunks.append((kind, source_bin + png_bytes))
        else:
            replaced_chunks.append((kind, payload))
    if not any(kind == JSON_CHUNK for kind, _ in replaced_chunks):
        raise ValueError("source JSON chunk disappeared")
    output_bytes = serialize_glb(document, replaced_chunks)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(output_bytes)

    output_document, output_chunks = read_glb(output_path)
    output_bin = next((payload for kind, payload in output_chunks if kind == BIN_CHUNK), None)
    normalized_materials = copy.deepcopy(output_document.get("materials", []))
    if original_texture_index is None:
        normalized_materials[material_index].get("pbrMetallicRoughness", {}).pop("baseColorTexture", None)
    else:
        normalized_materials[material_index]["pbrMetallicRoughness"]["baseColorTexture"]["index"] = original_texture_index

    binding = output_document["materials"][material_index]["pbrMetallicRoughness"]["baseColorTexture"]
    output_texture = output_document["textures"][int(binding["index"])]
    output_sampler = output_document.get("samplers", [])[int(output_texture["sampler"])] if "sampler" in output_texture else {}
    sampler_semantics = {
        "wrapS": int(output_sampler.get("wrapS", REPEAT)),
        "wrapT": int(output_sampler.get("wrapT", REPEAT)),
        "magFilter": int(output_sampler.get("magFilter", 9729)),
        "minFilter": int(output_sampler.get("minFilter", 9987)),
    }
    expected_sampler_semantics = {
        "wrapS": int(old_sampler.get("wrapS", REPEAT)),
        "wrapT": int(old_sampler.get("wrapT", REPEAT)),
        "magFilter": int(old_sampler.get("magFilter", 9729)),
        "minFilter": int(old_sampler.get("minFilter", 9987)),
    } if original_texture_index is not None else {
        "wrapS": REPEAT, "wrapT": REPEAT, "magFilter": 9729, "minFilter": 9987,
    }
    material_extensions_preserved = document["materials"][material_index].get("extensions", {}) \
        == source_document["materials"][material_index].get("extensions", {})
    extensions_used_preserved = document.get("extensionsUsed", []) == source_document.get("extensionsUsed", [])
    base_color_factor_preserved = document["materials"][material_index].get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1]) \
        == source_document["materials"][material_index].get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1])
    original_sampler_reused = sampler_index is None or sampler_index == int(output_texture.get("sampler", -1))
    texture_view = output_document["bufferViews"][int(output_document["images"][image_index]["bufferView"])]
    embedded_png_matches = output_bin is not None and output_bin[
        int(texture_view["byteOffset"]):int(texture_view["byteOffset"]) + int(texture_view["byteLength"])
    ] == png_bytes
    invariants = {
        "meshes_identical": output_document.get("meshes", []) == source_document.get("meshes", []),
        "accessors_identical": output_document.get("accessors", []) == source_document.get("accessors", []),
        "nodes_identical": output_document.get("nodes", []) == source_document.get("nodes", []),
        "scenes_identical": output_document.get("scenes", []) == source_document.get("scenes", []),
        "materials_identical_except_basecolor_texture_index": normalized_materials == old_materials,
        "original_buffer_views_identical": output_document.get("bufferViews", [])[:old_view_count]
        == source_document.get("bufferViews", []),
        "original_textures_identical": output_document.get("textures", [])[:old_texture_count]
        == source_document.get("textures", []),
        "original_images_identical": output_document.get("images", [])[:old_image_count]
        == source_document.get("images", []),
        "source_binary_prefix_identical": output_bin is not None and output_bin[:len(source_bin)] == source_bin,
        "embedded_png_bytes_identical": embedded_png_matches,
        "material_extensions_preserved": material_extensions_preserved,
        "extensions_used_preserved": extensions_used_preserved,
        "base_color_factor_preserved": base_color_factor_preserved,
        "sampler_semantics_preserved": sampler_semantics == expected_sampler_semantics,
        "original_sampler_reused": original_sampler_reused,
        "source_unchanged": sha256_file(source_path) == source_hash_before,
    }
    all_invariants = all(invariants.values())
    report = {
        "protocol": "fresh-c-glb-basecolor-byte-preserving-patch-v1",
        "status": "PASS" if all_invariants and sampler_semantics["wrapS"] == REPEAT and sampler_semantics["wrapT"] == REPEAT else "FAIL",
        "source_glb": str(source_path),
        "source_glb_sha256": source_hash_before,
        "output_glb": str(output_path),
        "output_glb_sha256": sha256_file(output_path),
        "texture_png": str(texture_path),
        "texture_png_sha256": sha256_file(texture_path),
        "material_index": material_index,
        "original_basecolor_texture_index": original_texture_index,
        "output_basecolor_texture_index": int(binding["index"]),
        "sampler_semantics": sampler_semantics,
        "material_extensions_preserved": material_extensions_preserved,
        "extensions_used_preserved": extensions_used_preserved,
        "base_color_factor_preserved": base_color_factor_preserved,
        "original_sampler_reused": original_sampler_reused,
        "original_sampler": old_sampler,
        "original_glb_binary_prefix_sha256": sha256_bytes(source_bin),
        "output_glb_binary_prefix_sha256": sha256_bytes(output_bin[:len(source_bin)]) if output_bin is not None else None,
        "invariants": invariants,
        "all_invariants_pass": all_invariants,
        "no_mesh_reexport_or_uv_reparameterization": True,
    }
    sidecar = output_path.with_suffix(output_path.suffix + ".patch.json")
    sidecar.write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] != "PASS":
        raise RuntimeError(f"byte-preserving GLB patch verification failed; see {sidecar}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--texture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--material-index", type=int, default=0)
    parser.add_argument("--name", default=None)
    args = parser.parse_args()
    print(json.dumps(patch_basecolor_texture(args.source, args.texture, args.output,
                                             args.material_index, args.name), indent=2))


if __name__ == "__main__":
    main()
