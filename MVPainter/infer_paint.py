
import os 
from glob import glob
from scripts.remesh_reduce_blender_script import remesh_and_replace,reduce_mesh
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--mv_res_dir', type=str, default='./outputs/test/mvpainter', help='input directory.')
parser.add_argument('--output_dir', type=str, default='./results/test/mvpainter', help='output directory.')
parser.add_argument('--geo_rotation', type=int, default=-90)



args = parser.parse_args()
input_dir = args.mv_res_dir
save_path=args.output_dir


# # 上采样/减面
# objs = glob(os.path.join(input_dir,'*','blender.obj'))
# print(os.path.join(input_dir,'*','blender.obj'))
# for obj in objs:
#     # remesh_and_replace(obj,voxel_size=0.003)
#     if os.path.exists(obj.replace('.obj','_low.obj')):
#         continue
#     reduce_mesh(obj,target_vertices=30000,output_path=obj.replace('.obj','_low.obj'))



# 烘焙贴图
cmd = f'''
cd mvpainter/ && \
python bake_pipeline.py --input_dir {input_dir} --save_dir {os.path.join(save_path,'glbs')} --offset {args.geo_rotation + 90}
'''
os.system(cmd)




# # 烘焙贴图
# cmd = f'''
# cd mvpainter/ && \
# python bake_pipeline_mvadapter.py --input_dir {input_dir} --save_dir {os.path.join(save_path,'glbs')}
# '''
# os.system(cmd)


