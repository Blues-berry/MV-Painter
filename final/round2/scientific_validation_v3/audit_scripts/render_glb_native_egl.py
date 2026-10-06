#!/usr/bin/env python3
"""Render stored bake GLBs with their embedded glTF base-color sampler.

This audit evaluates the exported texture result as stored. It does not rebake
textures or modify the production bake pipeline. Rendering is texture-only
(unlit base color) so the pixels remain comparable to the frozen CPU metrics.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import io
import json
import math
import os
import struct
from pathlib import Path

import numpy as np
os.environ["PYOPENGL_PLATFORM"] = "egl"
import pyrender
from PIL import Image
from OpenGL.GL import *
from OpenGL.raw.GL.VERSION.GL_1_1 import (
    glGenTextures as raw_gen_textures,
    glDeleteTextures as raw_delete_textures,
)
from OpenGL.raw.GL.VERSION.GL_1_5 import (
    glGenBuffers as raw_gen_buffers,
    glDeleteBuffers as raw_delete_buffers,
)
from OpenGL.raw.GL.VERSION.GL_3_0 import (
    glGenFramebuffers as raw_gen_framebuffers,
    glDeleteFramebuffers as raw_delete_framebuffers,
    glGenRenderbuffers as raw_gen_renderbuffers,
    glDeleteRenderbuffers as raw_delete_renderbuffers,
    glGenVertexArrays as raw_gen_vertex_arrays,
    glDeleteVertexArrays as raw_delete_vertex_arrays,
)


V3 = Path(__file__).resolve().parents[1]
BAKE = V3 / "bake_handoff"
DEFAULT_OUTPUT = BAKE / "GLB_NATIVE_EGL_RENDER_V1"
FILTERS = {
    9728: GL_NEAREST,
    9729: GL_LINEAR,
    9984: GL_NEAREST_MIPMAP_NEAREST,
    9985: GL_LINEAR_MIPMAP_NEAREST,
    9986: GL_NEAREST_MIPMAP_LINEAR,
    9987: GL_LINEAR_MIPMAP_LINEAR,
}
WRAPS = {
    33071: GL_CLAMP_TO_EDGE,
    33648: GL_MIRRORED_REPEAT,
    10497: GL_REPEAT,
}
COMPONENTS = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": 4,
    "MAT3": 9,
    "MAT4": 16,
}
DTYPES = {
    5120: np.dtype("i1"),
    5121: np.dtype("u1"),
    5122: np.dtype("<i2"),
    5123: np.dtype("<u2"),
    5125: np.dtype("<u4"),
    5126: np.dtype("<f4"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def raw_gen(function) -> int:
    value = (ctypes.c_uint * 1)()
    function(1, value)
    return int(value[0])


def raw_delete(function, value: int) -> None:
    values = (ctypes.c_uint * 1)(int(value))
    function(1, values)


def read_glb(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise ValueError(f"invalid GLB header: {path}")
    offset = 12
    document = None
    binary = None
    while offset < len(data):
        size, chunk_type = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunk = data[offset : offset + size]
        offset += size
        if chunk_type == b"JSON":
            document = json.loads(chunk.decode("utf-8").rstrip("\x00 \t\r\n"))
        elif chunk_type == b"BIN\x00":
            binary = chunk
    if document is None or binary is None:
        raise ValueError(f"GLB needs JSON and BIN chunks: {path}")
    return document, binary


def accessor(document: dict, binary: bytes, index: int) -> np.ndarray:
    spec = document["accessors"][index]
    if "sparse" in spec:
        raise ValueError("sparse accessors are outside this frozen output schema")
    view = document["bufferViews"][spec["bufferView"]]
    if view.get("buffer", 0) != 0:
        raise ValueError("GLB accessor refers to a non-embedded buffer")
    dtype = DTYPES[spec["componentType"]]
    width = COMPONENTS[spec["type"]]
    itemsize = dtype.itemsize
    stride = int(view.get("byteStride", width * itemsize))
    start = int(view.get("byteOffset", 0)) + int(spec.get("byteOffset", 0))
    raw = np.ndarray(
        (int(spec["count"]), width),
        dtype=dtype,
        buffer=binary,
        offset=start,
        strides=(stride, itemsize),
    ).copy()
    if spec.get("normalized", False):
        if np.issubdtype(dtype, np.unsignedinteger):
            raw = raw.astype(np.float32) / np.iinfo(dtype).max
        elif np.issubdtype(dtype, np.signedinteger):
            raw = np.maximum(raw.astype(np.float32) / np.iinfo(dtype).max, -1.0)
        else:
            raise ValueError("normalized floating-point accessor")
    return raw


def node_matrix(node: dict) -> np.ndarray:
    if "matrix" in node:
        return np.asarray(node["matrix"], dtype=np.float64).reshape(4, 4, order="F")
    translation = np.asarray(node.get("translation", [0, 0, 0]), dtype=np.float64)
    scale = np.asarray(node.get("scale", [1, 1, 1]), dtype=np.float64)
    x, y, z, w = np.asarray(node.get("rotation", [0, 0, 0, 1]), dtype=np.float64)
    rotation = np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=np.float64,
    )
    matrix = np.eye(4, dtype=np.float64)
    matrix[:3, :3] = rotation @ np.diag(scale)
    matrix[:3, 3] = translation
    return matrix


def native_asset(path: Path, record: dict) -> dict:
    document, binary = read_glb(path)
    scene_index = int(document.get("scene", 0))
    scene = document["scenes"][scene_index]
    positions_all = []
    uv_all = []
    faces_all = []
    source_vertices = []
    material_indices = set()

    def visit(node_index: int, parent: np.ndarray) -> None:
        node = document["nodes"][node_index]
        transform = parent @ node_matrix(node)
        if "mesh" in node:
            mesh = document["meshes"][node["mesh"]]
            for primitive in mesh["primitives"]:
                if int(primitive.get("mode", 4)) != 4:
                    raise ValueError("only triangle primitives are supported")
                attributes = primitive["attributes"]
                if "POSITION" not in attributes or "TEXCOORD_0" not in attributes:
                    raise ValueError("primitive lacks POSITION or TEXCOORD_0")
                if primitive.get("material") is None:
                    raise ValueError("unmaterialed primitive in baked GLB")
                material_indices.add(int(primitive["material"]))
                positions = accessor(document, binary, attributes["POSITION"]).astype(np.float64)
                uv = accessor(document, binary, attributes["TEXCOORD_0"]).astype(np.float32)
                if positions.shape != (len(uv), 3) or uv.shape[1] != 2:
                    raise ValueError("unexpected vertex/UV accessor shape")
                homogeneous = np.column_stack([positions, np.ones(len(positions))])
                gltf_world = (homogeneous @ transform.T)[:, :3]
                # glTF output nodes encode the Blender-to-glTF Y-up basis. The
                # frozen handoff cameras and normalization use Blender axes.
                handoff_world = np.column_stack(
                    [gltf_world[:, 0], -gltf_world[:, 2], gltf_world[:, 1]]
                )
                source_vertices.append(handoff_world)
                indices = (
                    accessor(document, binary, primitive["indices"]).reshape(-1)
                    if "indices" in primitive
                    else np.arange(len(positions), dtype=np.uint32)
                )
                if len(indices) % 3:
                    raise ValueError("triangle index list length is not divisible by three")
                base = sum(len(array) for array in positions_all)
                positions_all.append(handoff_world.astype(np.float32))
                uv_all.append(uv)
                faces_all.append(indices.astype(np.uint32).reshape(-1, 3) + base)
        for child in node.get("children", []):
            visit(int(child), transform)

    for root_node in scene["nodes"]:
        visit(int(root_node), np.eye(4, dtype=np.float64))

    if len(material_indices) != 1:
        raise ValueError(f"expected one baked material, found {sorted(material_indices)}")
    source_vertices = np.concatenate(source_vertices, axis=0)
    expected_bbox = record["blender_audit_bbox"]
    bbox_error = max(
        float(np.max(np.abs(source_vertices.min(axis=0) - expected_bbox["bbox_min"]))),
        float(np.max(np.abs(source_vertices.max(axis=0) - expected_bbox["bbox_max"]))),
    )
    if not math.isfinite(bbox_error) or bbox_error > 1e-2:
        raise ValueError(f"handoff-space GLB bbox differs from frozen audit by {bbox_error:g}")

    norm = record["normalization"]
    scale = float(norm["scale"])
    offset = np.asarray(norm["offset"], dtype=np.float32)
    normalized_positions = [scale * (part + offset) for part in positions_all]
    positions = np.concatenate(normalized_positions).astype(np.float32)
    uv = np.concatenate(uv_all).astype(np.float32)
    faces = np.concatenate(faces_all).astype(np.uint32)
    if not (np.isfinite(positions).all() and np.isfinite(uv).all()):
        raise ValueError("non-finite vertex or UV coordinate in baked GLB")

    material = document["materials"][next(iter(material_indices))]
    if material.get("alphaMode", "OPAQUE") != "OPAQUE":
        raise ValueError("only OPAQUE baked materials are supported")
    pbr = material.get("pbrMetallicRoughness", {})
    binding = pbr.get("baseColorTexture")
    if not binding or int(binding.get("texCoord", 0)) != 0:
        raise ValueError("baked material must use baseColorTexture TEXCOORD_0")
    texture_spec = document["textures"][int(binding["index"])]
    image_spec = document["images"][int(texture_spec["source"])]
    if "bufferView" not in image_spec:
        raise ValueError("baked base-color image is not embedded in the GLB")
    image_view = document["bufferViews"][int(image_spec["bufferView"])]
    image_start = int(image_view.get("byteOffset", 0))
    image_payload = binary[image_start : image_start + int(image_view["byteLength"])]
    image = np.asarray(Image.open(io.BytesIO(image_payload)).convert("RGBA"))
    if image.ndim != 3 or image.shape[2] != 4:
        raise ValueError("embedded base-color image did not decode as RGBA")
    sampler_index = texture_spec.get("sampler")
    sampler = document.get("samplers", [])[int(sampler_index)] if sampler_index is not None else {}
    wrap_s = int(sampler.get("wrapS", 10497))
    wrap_t = int(sampler.get("wrapT", 10497))
    mag_filter = int(sampler.get("magFilter", 9729))
    min_filter = int(sampler.get("minFilter", 9987))
    if any(value not in WRAPS for value in (wrap_s, wrap_t)):
        raise ValueError(f"unsupported sampler wrapping: {wrap_s}/{wrap_t}")
    if mag_filter not in FILTERS or min_filter not in FILTERS:
        raise ValueError(f"unsupported sampler filtering: {mag_filter}/{min_filter}")
    factor = np.asarray(pbr.get("baseColorFactor", [1, 1, 1, 1]), dtype=np.float32)
    return {
        "document": document,
        "positions": positions,
        "uv": uv,
        "faces": faces,
        "image": image,
        "wrap_s": wrap_s,
        "wrap_t": wrap_t,
        "mag_filter": mag_filter,
        "min_filter": min_filter,
        "base_color_factor": factor,
        "bbox_error": bbox_error,
        "source_vertex_count": int(len(positions)),
        "triangle_count": int(len(faces)),
    }


def compile_shader(kind: int, source: str) -> int:
    shader = glCreateShader(kind)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode("utf-8", "replace"))
    return int(shader)


VERTEX_SHADER = """#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec2 texcoord;
uniform vec3 camera_row0;
uniform vec3 camera_row1;
uniform vec3 camera_row2;
uniform vec3 camera_translation;
uniform vec2 camera_near_far;
out vec2 uv;
void main() {
    vec3 p = vec3(dot(camera_row0, position), dot(camera_row1, position),
                  dot(camera_row2, position)) + camera_translation;
    float z = 2.0 * (p.z - camera_near_far.x) /
              (camera_near_far.y - camera_near_far.x) - 1.0;
    gl_Position = vec4(2.0 * p.x, -2.0 * p.y, z, 1.0);
    uv = texcoord;
}
"""

FRAGMENT_SHADER = """#version 330 core
in vec2 uv;
out vec4 color;
uniform sampler2D base_color;
uniform vec4 base_color_factor;
vec3 linear_to_srgb(vec3 x) {
    x = max(x, vec3(0.0));
    return mix(12.92 * x, 1.055 * pow(x, vec3(1.0 / 2.4)) - 0.055,
               step(vec3(0.0031308), x));
}
void main() {
    vec3 linear_rgb = texture(base_color, uv).rgb * base_color_factor.rgb;
    color = vec4(linear_to_srgb(linear_rgb), 1.0);
}
"""


class EGLBaseColorRenderer:
    def __init__(self, resolution: int):
        self.resolution = int(resolution)
        self.context = pyrender.OffscreenRenderer(self.resolution, self.resolution)
        self.context._platform.make_current()
        self.vendor = glGetString(GL_VENDOR).decode("utf-8", "replace")
        self.renderer = glGetString(GL_RENDERER).decode("utf-8", "replace")
        self.version = glGetString(GL_VERSION).decode("utf-8", "replace")

        program = glCreateProgram()
        glAttachShader(program, compile_shader(GL_VERTEX_SHADER, VERTEX_SHADER))
        glAttachShader(program, compile_shader(GL_FRAGMENT_SHADER, FRAGMENT_SHADER))
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(program).decode("utf-8", "replace"))
        self.program = int(program)

        self.framebuffer = raw_gen(raw_gen_framebuffers)
        self.color_target = raw_gen(raw_gen_textures)
        glBindTexture(GL_TEXTURE_2D, self.color_target)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA8, self.resolution, self.resolution,
            0, GL_RGBA, GL_UNSIGNED_BYTE, None,
        )
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_target, 0
        )
        self.depth_target = raw_gen(raw_gen_renderbuffers)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_target)
        glRenderbufferStorage(
            GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, self.resolution, self.resolution
        )
        glFramebufferRenderbuffer(
            GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depth_target
        )
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("EGL color/depth framebuffer is incomplete")

        self.vertex_array = raw_gen(raw_gen_vertex_arrays)
        self.vertex_buffer = raw_gen(raw_gen_buffers)
        self.index_buffer = raw_gen(raw_gen_buffers)
        glBindVertexArray(self.vertex_array)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        self.texture = None
        self.index_count = 0
        self.base_color_factor = np.ones(4, dtype=np.float32)
        self.sampler_probe = self._verify_sampler_semantics()

    def _verify_sampler_semantics(self) -> dict:
        # A synthetic asymmetric 2x2 texture pins top-down PNG upload, glTF
        # (0,0) orientation, and repeat addressing before any study render.
        probe_texture = raw_gen(raw_gen_textures)
        glBindTexture(GL_TEXTURE_2D, probe_texture)
        image = np.asarray(
            [
                [[255, 0, 0, 255], [0, 255, 0, 255]],
                [[0, 0, 255, 255], [255, 255, 0, 255]],
            ],
            dtype=np.uint8,
        )
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 2, 2, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        vertex = """#version 330 core
        void main() {
            vec2 p[3] = vec2[3](vec2(-1,-1), vec2(3,-1), vec2(-1,3));
            gl_Position = vec4(p[gl_VertexID], 0, 1);
        }
        """
        fragment = """#version 330 core
        out vec4 color;
        uniform sampler2D source_texture;
        uniform vec2 source_uv;
        void main() { color = texture(source_texture, source_uv); }
        """
        program = glCreateProgram()
        glAttachShader(program, compile_shader(GL_VERTEX_SHADER, vertex))
        glAttachShader(program, compile_shader(GL_FRAGMENT_SHADER, fragment))
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(program).decode("utf-8", "replace"))
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glViewport(0, 0, self.resolution, self.resolution)
        glDisable(GL_DEPTH_TEST)
        glUseProgram(program)
        glBindVertexArray(self.vertex_array)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, probe_texture)
        glUniform1i(glGetUniformLocation(program, "source_texture"), 0)
        cases = {
            "top_left": ((0.25, 0.25), [255, 0, 0, 255]),
            "top_right": ((0.75, 0.25), [0, 255, 0, 255]),
            "bottom_left": ((0.25, 0.75), [0, 0, 255, 255]),
            "bottom_right": ((0.75, 0.75), [255, 255, 0, 255]),
            "repeat_negative_u": ((-0.25, 0.25), [0, 255, 0, 255]),
            "repeat_u_above_one": ((1.25, 0.25), [255, 0, 0, 255]),
        }
        observed = {}
        for name, (coordinate, expected) in cases.items():
            glUniform2f(glGetUniformLocation(program, "source_uv"), *coordinate)
            glDrawArrays(GL_TRIANGLES, 0, 3)
            pixel = np.frombuffer(
                glReadPixels(
                    self.resolution // 2,
                    self.resolution // 2,
                    1,
                    1,
                    GL_RGBA,
                    GL_UNSIGNED_BYTE,
                ),
                dtype=np.uint8,
            ).tolist()
            observed[name] = pixel
            if pixel != expected:
                raise RuntimeError(f"sampler orientation/wrap probe failed at {name}: {pixel}")
        glDeleteProgram(program)
        raw_delete(raw_delete_textures, probe_texture)
        glEnable(GL_DEPTH_TEST)
        return {"status": "PASS", "observed_rgba8": observed}

    def _upload_asset(self, asset: dict) -> None:
        glBindVertexArray(self.vertex_array)
        vertices = np.concatenate([asset["positions"], asset["uv"]], axis=1).astype(np.float32)
        indices = asset["faces"].reshape(-1).astype(np.uint32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        self.index_count = int(len(indices))

        self.texture = raw_gen(raw_gen_textures)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        image = np.ascontiguousarray(asset["image"])
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_SRGB8_ALPHA8, image.shape[1], image.shape[0],
            0, GL_RGBA, GL_UNSIGNED_BYTE, image,
        )
        if asset["min_filter"] in (9984, 9985, 9986, 9987):
            glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, FILTERS[asset["mag_filter"]])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, FILTERS[asset["min_filter"]])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, WRAPS[asset["wrap_s"]])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, WRAPS[asset["wrap_t"]])

    def prepare_asset(self, asset: dict) -> None:
        self.context._platform.make_current()
        if self.texture is not None:
            raw_delete(raw_delete_textures, self.texture)
            self.texture = None
        self._upload_asset(asset)
        self.base_color_factor = asset["base_color_factor"]

    def render(self, camera: dict) -> np.ndarray:
        if self.texture is None:
            raise RuntimeError("prepare_asset must be called before rendering")
        self.context._platform.make_current()
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glViewport(0, 0, self.resolution, self.resolution)
        glDisable(GL_BLEND)
        glDisable(GL_CULL_FACE)
        glDisable(GL_FRAMEBUFFER_SRGB)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glDepthMask(GL_TRUE)
        glClearColor(1.0, 1.0, 1.0, 0.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program)
        glBindVertexArray(self.vertex_array)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniform1i(glGetUniformLocation(self.program, "base_color"), 0)
        glUniform4fv(
            glGetUniformLocation(self.program, "base_color_factor"),
            1,
            self.base_color_factor,
        )
        extrinsic = np.asarray(camera["extrinsic"], dtype=np.float32)
        for row, name in enumerate(("camera_row0", "camera_row1", "camera_row2")):
            glUniform3fv(
                glGetUniformLocation(self.program, name), 1, extrinsic[row, :3]
            )
        glUniform3fv(
            glGetUniformLocation(self.program, "camera_translation"),
            1,
            extrinsic[:, 3],
        )
        glUniform2f(
            glGetUniformLocation(self.program, "camera_near_far"),
            float(camera["near"]),
            float(camera["far"]),
        )
        if not str(camera.get("camera", "ortho")).lower().startswith("ortho"):
            raise ValueError("frozen handoff contains a non-orthographic camera")
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glFinish()
        raw = glReadPixels(
            0, 0, self.resolution, self.resolution, GL_RGBA, GL_UNSIGNED_BYTE
        )
        return np.frombuffer(raw, dtype=np.uint8).reshape(
            self.resolution, self.resolution, 4
        )[::-1].copy()

    def close(self) -> None:
        self.context._platform.make_current()
        if self.texture is not None:
            raw_delete(raw_delete_textures, self.texture)
            self.texture = None
        raw_delete(raw_delete_buffers, self.vertex_buffer)
        raw_delete(raw_delete_buffers, self.index_buffer)
        raw_delete(raw_delete_vertex_arrays, self.vertex_array)
        raw_delete(raw_delete_renderbuffers, self.depth_target)
        raw_delete(raw_delete_framebuffers, self.framebuffer)
        raw_delete(raw_delete_textures, self.color_target)
        glDeleteProgram(self.program)
        self.context.delete()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--objects", help="comma-separated frozen object IDs")
    parser.add_argument("--methods", help="comma-separated baked GLB condition names")
    parser.add_argument("--views", default=",".join(str(i) for i in range(1, 12)))
    parser.add_argument("--resolution", type=int, default=512)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    handoff_path = BAKE / "BAKE_INPUT_HANDOFF_V3.json"
    run_path = BAKE / "cpu_bake_v3/BAKE_RUN_SUMMARY.json"
    excluded_path = BAKE / "excluded_uv_missing.json"
    handoff = json.loads(handoff_path.read_text())
    run = json.loads(run_path.read_text())
    excluded = set(json.loads(excluded_path.read_text()))
    records = {item["object"]: item for item in handoff["objects"]}
    requested_objects = (
        [x.strip() for x in args.objects.split(",") if x.strip()]
        if args.objects
        else sorted(set(records) - excluded)
    )
    methods = (
        [x.strip() for x in args.methods.split(",") if x.strip()]
        if args.methods
        else list(run["methods"])
    )
    views = [int(x.strip()) for x in args.views.split(",") if x.strip()]
    if any(view < 0 or view >= len(handoff["objects"][0]["camera_poses_17"]) for view in views):
        raise SystemExit("requested raw view index is outside the frozen camera list")
    if not requested_objects or not methods or not views:
        raise SystemExit("objects, methods, and views must all be non-empty")
    if set(methods) - set(run["methods"]):
        raise SystemExit(f"methods not present in bake run: {sorted(set(methods) - set(run['methods']))}")
    if set(requested_objects) - (set(records) - excluded):
        raise SystemExit("requested object is absent from the supported frozen UV cohort")

    method_objects = {
        method: {path.name for path in (BAKE / "cpu_bake_v3" / method).iterdir() if path.is_dir()}
        for method in methods
    }
    if any(set(requested_objects) - values for values in method_objects.values()):
        raise SystemExit("one or more requested object/method GLBs are missing")

    renderer = EGLBaseColorRenderer(args.resolution)
    manifest_rows = []
    object_errors = {}
    try:
        for method in methods:
            for uid in requested_objects:
                record = records[uid]
                method_dir = BAKE / "cpu_bake_v3" / method / uid
                glb_path = method_dir / f"{uid}_{method}_textured.glb"
                metadata_path = method_dir / "bake_metadata.json"
                asset = native_asset(glb_path, record)
                object_errors[uid] = max(object_errors.get(uid, 0.0), asset["bbox_error"])
                renderer.prepare_asset(asset)
                destination = output / method / uid
                destination.mkdir(parents=True, exist_ok=True)
                (destination / "bake_metadata.json").write_bytes(metadata_path.read_bytes())
                for raw_view in views:
                    rendered = renderer.render(record["camera_poses_17"][raw_view])
                    image_path = destination / "unseen_renders" / f"view_{raw_view:03d}.png"
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    Image.fromarray(rendered, mode="RGBA").save(image_path, compress_level=6)
                    manifest_rows.append(
                        {
                            "object": uid,
                            "method": method,
                            "raw_view": raw_view,
                            "source_glb": str(glb_path),
                            "source_glb_sha256": sha256(glb_path),
                            "source_bake_metadata_sha256": sha256(metadata_path),
                            "render_path": str(image_path.relative_to(output)),
                            "render_sha256": sha256(image_path),
                            "sampler": {
                                "wrapS": asset["wrap_s"],
                                "wrapT": asset["wrap_t"],
                                "magFilter": asset["mag_filter"],
                                "minFilter": asset["min_filter"],
                            },
                            "image_size": list(asset["image"].shape[1::-1]),
                            "vertex_count": asset["source_vertex_count"],
                            "triangle_count": asset["triangle_count"],
                            "handoff_bbox_max_abs_error": asset["bbox_error"],
                            "camera_sha256": hashlib.sha256(
                                json.dumps(
                                    record["camera_poses_17"][raw_view],
                                    sort_keys=True,
                                    separators=(",", ":"),
                                ).encode()
                            ).hexdigest(),
                        }
                    )
    finally:
        renderer.close()

    manifest = {
        "protocol": "glb-native-basecolor-egl-render-v1",
        "interpretation": "embedded GLB baseColorTexture; unlit and texture-only; not a full PBR viewer render",
        "scene_semantics": {
            "GLB_sampler": "embedded sampler with glTF defaults when fields are omitted",
            "texture_color_space": "sRGB base-color image sampled as GL_SRGB8_ALPHA8; linear result encoded to sRGB output",
            "UV_origin": "glTF accessor coordinates used without V inversion; PNG rows uploaded top-down",
            "depth": "24-bit depth attachment; orthographic projection from frozen handoff camera",
            "basis": "GLB scene coordinates mapped to handoff Blender axes as (x, -z, y), bbox checked against frozen Blender audit",
            "mesh_normalization": "frozen handoff scale * (source_world + offset)",
            "bake_inputs_changed": False,
            "production_bake_rerun": False,
        },
        "renderer": {
            "backend": "EGL / PyOpenGL",
            "vendor": renderer.vendor,
            "device": renderer.renderer,
            "version": renderer.version,
            "resolution": args.resolution,
            "sampler_probe": renderer.sampler_probe,
        },
        "handoff_sha256": sha256(handoff_path),
        "bake_run_summary_sha256": sha256(run_path),
        "renderer_script_sha256": sha256(Path(__file__).resolve()),
        "frozen_cohort_n": len(handoff["objects"]),
        "prebake_no_uv_exclusions": sorted(excluded),
        "rendered_objects": requested_objects,
        "rendered_methods": methods,
        "raw_views": views,
        "object_bbox_max_abs_errors": object_errors,
        "render_count": len(manifest_rows),
        "renders": manifest_rows,
    }
    (output / "GLB_NATIVE_EGL_RENDER_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {key: manifest[key] for key in (
                "protocol", "renderer", "frozen_cohort_n", "prebake_no_uv_exclusions",
                "rendered_objects", "rendered_methods", "raw_views", "render_count",
                "object_bbox_max_abs_errors",
            )},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
