import trimesh
import xatlas


def mesh_uv_wrap(mesh):
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)


    vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)

    mesh.vertices = mesh.vertices[vmapping]
    mesh.faces = indices
    mesh.visual.uv = uvs

    return mesh
