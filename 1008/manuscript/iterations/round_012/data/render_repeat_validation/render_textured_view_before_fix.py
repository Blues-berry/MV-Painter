def render_textured_view(
    geometry: dict,
    texture: np.ndarray,
    camera: dict,
    resolution: int,
    cache: dict,
    repeat_uv: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
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
        if repeat_uv:
            x = uv[:, 0] * size - 0.5
            y = (1.0 - uv[:, 1]) * size - 0.5
        else:
            x = np.clip(uv[:, 0], 0.0, 1.0) * (size - 1)
            y = np.clip(1.0 - uv[:, 1], 0.0, 1.0) * (size - 1)
        x0 = np.floor(x).astype(np.int32)
        y0 = np.floor(y).astype(np.int32)
        if repeat_uv:
            x0 = np.mod(x0, size)
            y0 = np.mod(y0, size)
            x1 = np.mod(x0 + 1, size)
            y1 = np.mod(y0 + 1, size)
        else:
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
