import OpenEXR
import Imath
from PIL import Image
import numpy as np
from tqdm import tqdm
import os
import json
import cv2
import argparse

from multiprocessing import Pool, cpu_count
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
def load_obj(file_path):
    vertices = []
    faces = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertex = list(map(float, line.strip().split()[1:]))
                vertices.append(vertex)
            elif line.startswith('f '):
                face = [int(vertex.split('/')[0]) - 1 for vertex in line.strip().split()[1:]]
                faces.append(face)
    return np.array(vertices), np.array(faces)
def depth_exr_to_png(exr_file, png_file, depth_channel='R', depth_scale=6.0):
    # print(png_file)
    exr_image = OpenEXR.InputFile(exr_file)
    header = exr_image.header()

    size = (header['displayWindow'].max.x + 1, header['displayWindow'].max.y + 1)

    depth_channel = exr_image.channel(depth_channel, Imath.PixelType(Imath.PixelType.FLOAT))

    depth_array = np.frombuffer(depth_channel, dtype=np.float32).copy()
    depth_array = depth_array.reshape((size[1], size[0]))

    invalid_mask = depth_array == 1.0

    depth_array /= depth_scale

    depth_array_uint8 = (depth_array * 65535).astype(np.uint16)
    depth_array_uint8[invalid_mask] = 65535

    depth_image = Image.fromarray(depth_array_uint8)

    depth_image.save(png_file)


def normal_exr_to_png(exr_file, png_file):
    normal = cv2.imread(exr_file, cv2.IMREAD_UNCHANGED)
    normal_unit8 = (normal * 255).astype(np.uint16)
    cv2.imwrite(png_file, normal_unit8)


def process(root_dir,depth_scale = 6.0,num_views = 32):
    all_uids = os.listdir(root_dir)



    pool = Pool(processes=cpu_count())
    args_list = [(uid, root_dir, depth_scale, num_views) for uid in all_uids]
    # process_uid(args_list[0])
    for _ in tqdm(pool.imap_unordered(process_uid, args_list), total=len(all_uids)):
        pass
    pool.close()
    pool.join()

            
            
def process_uid(args):

    uid, root_dir, depth_scale, num_views = args

    depth_exr_dir = os.path.join(root_dir,uid,'depth')
    depth_png_dir = os.path.join(root_dir,uid,'depth_png')

    os.makedirs(depth_png_dir,exist_ok=True)


    
    if not os.path.exists(depth_exr_dir):
        print(depth_exr_dir)
        print(f'no  depth in {uid}')
        return 

    flag = True
    for k in range(num_views):

        depth_exr_path = os.path.join(depth_exr_dir,f'{str(k).zfill(3)}.exr')
        depth_png_path = os.path.join(depth_png_dir,(f'{str(k).zfill(3)}.png'))
        if os.path.exists(depth_exr_path):
            depth_exr_to_png(depth_exr_path,depth_png_path,'R',depth_scale=depth_scale)
        else:
            print('no exr')
            flag = False

            break
    if flag:
        print("succeed")
    else:
        print("false")
    
   
    return


            


        
        



                

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_dir', type=str, help='Path to renderings.')
    args = parser.parse_args()
    sub_dirs = os.listdir(args.root_dir)
    for sub_dir in sub_dirs:
        cur_dir = os.path.join(args.root_dir,sub_dir)
        depth_scale = 1.0
        num_views = 17
        try:
            process(cur_dir,depth_scale,num_views)
        except Exception as e:
            print(e)