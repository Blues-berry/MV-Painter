
import os
import subprocess
from glob import glob
import json
import argparse
import random


def render(render_lines):
    # for uid in tqdm(lines):
    for uid,i  in (render_lines):
        print(i)
        object_uid = uid

        hdri_paths = glob(os.path.join(args.hdri_dir,'*.exr'))
        for hdri_path in hdri_paths:
            output_dir = args.output_root_dir
            output_dir = os.path.join(output_dir,os.path.basename(hdri_path).split('.')[0])
            print(os.path.join(output_dir, object_uid))
            if os.path.exists(os.path.join(output_dir, object_uid)): 
                if os.path.exists(os.path.join(output_dir, object_uid,"image","036.png")):
                    print("continue")
                    continue


            try:
                cmds = ['../blender-4.2.4-linux-x64/blender', "-noaudio" ,'--background','-Y','--python','blender_script.py','--','--object_path',i,'--object_uid',object_uid,'--output_dir',output_dir,'--hdri_path',hdri_path]

                print(" ".join(cmds))
                subprocess.run(cmds)
                # break
            except Exception as e:
                print(e)
                continue


parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to meta file.')
parser.add_argument('--hdri_dir', type=str, help='Enviroment lighting dir')

parser.add_argument('--output_root_dir', type=str, help='output root directory')
args = parser.parse_args()
mesh_path_file = args.path
mesh_paths = []

with open(mesh_path_file,'r') as f:
    data = f.readlines()
    for line in data:
        line = line.strip().replace("NaN", "-1")
        meta = eval(line)
        mesh_path = meta['glb_path'].replace('xlab-nas-2','workspace').replace('\n','').replace('\r','')
        mesh_uid = meta['glb_name']
        mesh_paths.append((mesh_uid,mesh_path))
import random
random.shuffle(mesh_paths)
CONCURRENT_NUM = 1
render(mesh_paths)
