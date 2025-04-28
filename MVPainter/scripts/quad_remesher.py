import bpy
import os
import shutil

def reset_scene() -> None:
    """Resets the scene to a clean state.

    Returns:
        None
    """
    # delete everything that isn't part of a camera or a light
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    # delete all the materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material, do_unlink=True)

    # delete all the textures
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture, do_unlink=True)

    # delete all the images
    for image in bpy.data.images:
        bpy.data.images.remove(image, do_unlink=True)



plugin_path = "/mnt/xlab-nas-1/shaomingqi.smq/projects/aigc3d_dev/aigc3d/开源/MVPainter/scripts/quad_remesher_1_2/__init__.py"
# 进入 Blender 的上下文
bpy.ops.wm.read_factory_settings(use_empty=True)

# 安装插件
bpy.ops.preferences.addon_install(filepath=plugin_path)
# 获取插件名称（通常是插件目录名或 .zip 解压后的目录名）
plugin_name = "quad_remesher_1_2"  # 替换为实际的插件名称
# 激活插件
bpy.ops.preferences.addon_enable(module=plugin_name)



enabled_addons = bpy.context.preferences.addons.keys()
print("已启用的插件：", enabled_addons)

reset_scene()
glb_path = '/mnt/xlab-nas-1/shaomingqi.smq/projects/aigc3d_dev/aigc3d/开源/MVPainter/results/test/mvpainter/glbs/0012.glb'

if glb_path.endswith('.obj'):
    bpy.ops.import_scene.obj(filepath=glb_path)
elif glb_path.endswith('.glb'):
    bpy.ops.import_scene.gltf(filepath=glb_path)

obj =  bpy.context.scene.objects[1]
print(bpy.context.scene.objects[1].type)
if obj.type =='MESH':

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    print("remesh")
    print("before remesh vertices:",len(obj.data.vertices))
    bpy.ops.qremesher.remesh()
    obj_new =  bpy.context.scene.objects[1]
    print(bpy.context.scene.objects)
    print("after remesh vertices:",len(obj_new.data.vertices))
    print("remesh done")
        
        # bpy.ops.export_scene.obj(filepath='test_remesher.obj', use_selection=False)





