import os 
from glob import glob
import subprocess
import argparse



def render_single(predict_glb_path,exp_name,geo_rotation=-90):
    basename = os.path.basename(predict_glb_path).split('.')[0]
    cmds = ['../../blender-4.2.9-linux-x64/blender', '--background', '-Y',
            '--python',
            '../../blender_render_eval.py', '--',
            '--object_path', f'{predict_glb_path}',
            '--output_dir',f'../eval_temp/{exp_name}/{basename}',
            '--azimuth_offset',f'{geo_rotation}'
            ]

    print(" ".join(cmds))
    subprocess.run(cmds)




def render(predict_glb_dir,exp_name):
    predict_glbs_paths = glob(os.path.join(predict_glb_dir,'*.glb'))
    for i,predict_glb in enumerate(predict_glbs_paths):
        render_single(predict_glb,exp_name)






if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument('--textured_glb_dir', type=str, help='input directory.')
    parser.add_argument('--exp_name', type=str, help='output directory.')
    parser.add_argument('--geo_rotation', type=int, default=-90)
    
    args = parser.parse_args()

    render(args.textured_glb_dir,args.exp_name,args.geo_roration)