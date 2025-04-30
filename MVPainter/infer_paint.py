
import os 
from glob import glob
from scripts.remesh_reduce_blender_script import remesh_and_replace,reduce_mesh
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--mv_res_dir', type=str, default='./outputs/test/mvpainter', help='input directory.')
parser.add_argument('--output_dir', type=str, default='./results/test/mvpainter', help='output directory.')
parser.add_argument('--geo_rotation', type=int, default=-90)
parser.add_argument('--use_pbr', action='store_true', help='Enable PBR painting')


args = parser.parse_args()
input_dir = args.mv_res_dir
save_path=args.output_dir
use_pbr = args.use_pbr

# 上采样/减面
objs = glob(os.path.join(input_dir,'*','blender.obj'))
print(os.path.join(input_dir,'*','blender.obj'))
for obj in objs:
    # remesh_and_replace(obj,voxel_size=0.003)
    if os.path.exists(obj.replace('.obj','_low.obj')):
        continue
    reduce_mesh(obj,target_vertices=30000,output_path=obj.replace('.obj','_low.obj'))


if not use_pbr:
    # 烘焙贴图
    cmd = f'''
    cd mvpainter/ && \
    python bake_pipeline.py --input_dir {input_dir} --save_dir {os.path.join(save_path,'glbs')} --offset {args.geo_rotation + 90}
    '''
    os.system(cmd)
else:
    # basecolor
    cmd = f'''
    cd mvpainter/ && \
    python bake_pipeline.py --input_dir {input_dir} --save_dir {os.path.join(save_path,'basecolor')} --offset {args.geo_rotation + 90} --suffix _basecolor
    '''
    os.system(cmd)

    cmd = f'''
    cd scripts && \
    python blender_bake.py --input_dir {os.path.join(save_path,'basecolor')} --save_dir {os.path.join(save_path,'basecolor_bake')}
    '''
    os.system(cmd)


    # metallic
    cmd = f'''
    cd mvpainter/ && \
    python bake_pipeline.py --input_dir {input_dir} --save_dir {os.path.join(save_path,'metallic')} --offset {args.geo_rotation + 90} --suffix _metallic
    '''
    os.system(cmd)


    cmd = f'''
    cd scripts && \
    python blender_bake.py --input_dir {os.path.join(save_path,'metallic')} --save_dir {os.path.join(save_path,'metallic_bake')}
    '''
    os.system(cmd)

    # roughness

    cmd = f'''
    cd mvpainter/ && \
    python bake_pipeline.py --input_dir {input_dir} --save_dir {os.path.join(save_path,'roughness')} --offset {args.geo_rotation + 90} --suffix _roughness
    '''
    os.system(cmd)

    cmd = f'''
    cd scripts && \
    python blender_bake.py --input_dir {os.path.join(save_path,'roughness')} --save_dir {os.path.join(save_path,'roughness_bake')}
    '''
    os.system(cmd)

    # expor pbr glb
    cmd = f'''
    ../blender-4.2.9-linux-x64/blender  --background -Y --python scripts/blender_pbr_glb.py -- --basecolor_dir {os.path.join(save_path,'basecolor_bake')} --metallic_dir {os.path.join(save_path,'metallic_bake')} --roughness_dir {os.path.join(save_path,'roughness_bake')} --output_dir {os.path.join(save_path,'combine_pbr')}
    '''
    os.system(cmd)






