

import json 
import os
import glob
import random
from PIL import Image
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from skimage.measure import shannon_entropy
from skimage.feature import graycomatrix, graycoprops

def calculate_color_entropy(image_path):
    # 转换到 HSV 颜色空间
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # 计算每个通道的直方图
    hist_h = cv2.calcHist([hsv_image], [0], None, [256], [0, 256])
    hist_s = cv2.calcHist([hsv_image], [1], None, [256], [0, 256])
    hist_v = cv2.calcHist([hsv_image], [2], None, [256], [0, 256])
    # 归一化直方图
    hist_h /= np.sum(hist_h)
    hist_s /= np.sum(hist_s)
    hist_v /= np.sum(hist_v)
    # 计算熵
    entropy_h = shannon_entropy(hist_h)
    entropy_s = shannon_entropy(hist_s)
    entropy_v = shannon_entropy(hist_v)
    # 返回平均熵作为颜色丰富度
    return (entropy_h + entropy_s + entropy_v) / 3
def calculate_sobel_in_alpha_region(image_path):
    """
    计算图像 alpha 区域内的 Sobel 梯度均值
    :param image_path: 图像路径（RGBA 格式）
    :return: alpha 区域内的梯度幅值均值
    """
    # 读取图像（确保包含 alpha 通道）
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # 读取 RGBA 图像
    if img is None:
        raise ValueError(f"无法读取图像：{image_path}")
    
    # 检查是否有 alpha 通道
    if img.shape[2] != 4:
        raise ValueError("图像不包含 alpha 通道！请提供 RGBA 图像。")
    
    # 提取 alpha 通道（通道索引为 3）
    alpha_channel = img[:, :, 3]
    
    # 提取灰度图（通过 RGB 通道转换）
    gray_image = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
    
    # 创建 alpha 区域的掩模（非零区域为 1，透明区域为 0）
    alpha_mask = (alpha_channel > 0).astype(np.uint8)
    
    # 应用掩模到灰度图像（将透明区域的像素值设为 0）
    masked_gray_image = cv2.bitwise_and(gray_image, gray_image, mask=alpha_mask)
    
    # 计算 Sobel 梯度
    sobel_x = cv2.Sobel(masked_gray_image, cv2.CV_64F, 1, 0, ksize=3)  # 水平方向
    sobel_y = cv2.Sobel(masked_gray_image, cv2.CV_64F, 0, 1, ksize=3)  # 垂直方向
    gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)  # 梯度幅值
    
    # 仅统计 alpha 有效区域内的梯度幅值
    valid_gradient_values = gradient_magnitude[alpha_mask > 0]
    gradient_mean = np.mean(valid_gradient_values) if valid_gradient_values.size > 0 else 0  # 防止空区域
    
    return gradient_mean

def set_white_background(image_path):
    # 打开图片
    img = Image.open(image_path)
    
    # 如果图片有透明度（RGBA模式）
    if img.mode == 'RGBA':
        # 创建一个白色的背景图，尺寸与原图相同
        white_bg = Image.new('RGB', img.size, (255, 255, 255))
        
        # 将原图和白色背景合成
        img_with_white_bg = Image.alpha_composite(white_bg.convert('RGBA'), img)
        
        # 转换为RGB模式，去除透明度
        img_with_white_bg = img_with_white_bg.convert('RGB')
        
        return img_with_white_bg
    else:
        # 如果图片本身没有透明度，直接返回
        return img
    
def vis_datasets(root_dir,num_object,num_of_views,output_path):
    meta_json = os.path.join(root_dir,'filtered_meta.json')
    with open(meta_json, 'r') as json_file:
        dirs = json.load(json_file)
    random.shuffle(dirs)
    
    dirs = dirs[:num_object]
    print(dirs)
    image_paths = []
    for num,subdir in enumerate(dirs):
        rgb_dir = os.path.join(root_dir,subdir,'image')
        rgb_paths = []
        for i in range(0,num_of_views):
            rgb_path = os.path.join(rgb_dir,f'000.png') 
            rgb_path2 = os.path.join(rgb_dir,f'014.png') 

            # normal_path = os.path.join(normal_dir,f'{str(i).zfill(3)}_normal0001.png') 
            
            rgb_paths.append(rgb_path)
            rgb_paths.append(rgb_path2)

            image1 = (os.path.join(rgb_dir,'000.png'))
            image2 = (os.path.join(rgb_dir,'014.png'))
            # res = predict_single([image1,image2])
            energy_1 = calculate_color_entropy(image1)
            energy_2 = calculate_color_entropy(image2)

            color_energy = energy_1 + energy_2

            energy_1 = calculate_sobel_in_alpha_region(image1)
            energy_2 = calculate_sobel_in_alpha_region(image2)
            texture_energy = energy_1 + energy_2
            print(num,' img1:',color_energy * 30, texture_energy)

            print(num,' img1:',color_energy * 30+ texture_energy)
            # normal_paths.append(normal_path)

        for x in rgb_paths:
            image_paths.append(x)
        # for x in normal_paths:
        #     image_paths.append(x)

    # load images
    num_of_views = num_of_views * 2
    images = []
    for i,image_path in tqdm(enumerate(image_paths)):
        # if 'metallic' in image_path:
        #     roughness_metallic_img = np.array(set_white_background(image_path))
        #     roughness_imgs = (roughness_metallic_img[:,:,1])
        #     metallic_imgs = (roughness_metallic_img[:,:,2])
        #     images.append(Image.fromarray(metallic_imgs))
        #     images.append(Image.fromarray(roughness_imgs))

        #     # print(roughness_metallic_img.shape)
        # else:
        images.append(set_white_background(image_path))

    images_per_col = len(images) // num_of_views
    max_height = max(image.size[1] for image in images)
    max_width = max(image.size[0] for image in images)
    result_width = max_width * num_of_views
    result_height = max_height * images_per_col
    result = Image.new("RGB", (result_width, result_height),color="white")
    for i, image in tqdm(enumerate(images)):
        row = i // num_of_views
        col = i % num_of_views
        result.paste(image, (col * max_width, row * max_height))

    result.save(output_path)

def vis_dataset_single_image(root_dir,num_of_views,output_dir):
    meta_json = os.path.join(root_dir,'train_meta.json')
    with open(meta_json, 'r') as json_file:
        dirs = json.load(json_file)
    meta_json = os.path.join(root_dir,'test_meta.json')
    with open(meta_json, 'r') as json_file:
        dirs += json.load(json_file)
    # random.shuffle(dirs)
    os.makedirs(output_dir,exist_ok=True)
    

    print(dirs)
    for subdir in dirs:
        image_paths = []
        rgb_dir = os.path.join(root_dir,subdir,'rgba')
        normal_dir = os.path.join(root_dir,subdir,'normals')
        rgb_paths = []
        normal_paths = []
        for i in range(0,num_of_views):
            rgb_path = os.path.join(rgb_dir,f'{str(i).zfill(3)}.png') 
            normal_path = os.path.join(normal_dir,f'{str(i).zfill(3)}_normal0001.png') 
            rgb_paths.append(rgb_path)
            normal_paths.append(normal_path)

        for x in rgb_paths:
            image_paths.append(x)
        for x in normal_paths:
            image_paths.append(x)
        
        # load images
        images = []
        for i,image_path in tqdm(enumerate(image_paths)):
            if 'metallic' in image_path:
                metallic_roughness_img = np.array(Image.open(image_path))
                print(metallic_roughness_img.shape)
                # roughness_imgs = metallic_roughness_img[1,:,:].repeat(3,1,1)
                # metallic_imgs = metallic_roughness_img[2,:,:].repeat(3,1,1)
                
            else:
                images.append(Image.open(image_path))
        images_per_col = len(images) // num_of_views
        max_height = max(image.size[1] for image in images)
        max_width = max(image.size[0] for image in images)
        result_width = max_width * num_of_views
        result_height = max_height * images_per_col
        result = Image.new("RGB", (result_width, result_height))
        for i, image in tqdm(enumerate(images)):
            row = i // num_of_views
            col = i % num_of_views
            result.paste(image, (col * max_width, row * max_height))
        uid = subdir.split('/')[0]
        lighting_name = subdir.split('/')[1]

        result.save(os.path.join(output_dir,f'{uid}_{lighting_name}.png'))

def read_line(line):
    line = line.strip().replace("NaN", "-1")
    meta = eval(line)
    mesh_path = meta['img_2501'].replace('workspace', 'xlab-nas-2').replace('\n', '').replace('\r', '').split('/')[:-1]
    mesh_path = '/'.join(mesh_path)
    return mesh_path

def calculate_score_one(args):
    path,num_images,valid_uids = args
    if not os.path.isdir(path):
        return None

    if valid_uids is None:
        valid_uids = []
    uid = os.path.basename(path)
    # paths = glob.glob(os.path.join(x,'*'))

    image1 = (os.path.join(path,'image','000.png'))
    image2 = (os.path.join(path,'image','014.png'))

    energy_1 = calculate_color_entropy(image1)
    energy_2 = calculate_color_entropy(image2)

    color_energy = energy_1 + energy_2

    energy_1 = calculate_sobel_in_alpha_region(image1)
    energy_2 = calculate_sobel_in_alpha_region(image2)
    texture_energy = energy_1 + energy_2
    return path,color_energy,texture_energy

def calculate_final_condition(args):
    path,_,_ = args
    image1 = (os.path.join(path,'image','000.png'))
    image2 = (os.path.join(path,'image','014.png'))

    ratio_1 = calculate_alpha_mask_ratio(image1)
    ratio_2 = calculate_alpha_mask_ratio(image2)
    condition_mask = ratio_1 > 0.0075 and ratio_2 > 0.0075
    return path,condition_mask

def get_high_score_paths(score_path):
    pool = Pool(processes=cpu_count())

    with open(score_path, 'r') as json_file:
        data = json.load(json_file)
    for i in range(len(data)):
        if data[i]['texture_score'] > 500:
            data[i]['total_score'] = 0
        else:
            data[i]['total_score'] = data[i]['color_score'] * 35 + data[i]['texture_score']
    sorted_data = sorted(data,key=lambda x: x['total_score'], reverse=True)

    print("get high score paths....")
    valid_data = sorted_data[:100000]


    args_list = [(uid['path'],1,None) for uid in valid_data]
    
    results = []


    for path,result in tqdm(pool.imap_unordered(calculate_final_condition, args_list), total=len(data)):
        if result:
            results.append(path)



    with open('/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture/filtered_meta.json', 'w') as json_file:
        json.dump(results, json_file)

    
    


def calculate_score(root_path):

    meta_json = os.path.join(root_path,'train_meta.json')
    with open(meta_json, 'r') as json_file:
        obj_paths = json.load(json_file)
    obj_paths = obj_paths
    pool = Pool(processes=cpu_count())
    args_list = [(uid,1,None) for uid in obj_paths]

    results = []

    for path,color_score,texture_score in tqdm(pool.imap_unordered(calculate_score_one, args_list), total=len(args_list)):
        
        results.append({'path':path,'color_score':color_score,'texture_score':texture_score})

    # 将列表保存为 JSON 文件
    with open("/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture/color_texutre_scores.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

      
def process(root_dir,train_ratio = 0.9, num_images = 32,crucial_path = None):
    # obj_paths = glob.glob(root_dir + '/*')  # 使用通配符*匹配所有子文件夹
    obj_paths = []
    pool = Pool(processes=cpu_count())

    with open(root_dir,'r') as f:
        data = f.readlines()
        # 使用多线程处理
        print("start processsing...")
        for result in tqdm(pool.imap_unordered(read_line, data), total=len(data)):
            obj_paths.append(result)
    
    # obj_paths = obj_paths[:50000]

    print("原始文件个数：",len(obj_paths))


    
    if crucial_path:
        with open(crucial_path, 'r') as json_file:
            valid_uids = json.load(json_file)
            print(valid_uids)
    else:
        valid_uids = None

    for x in obj_paths:
        pass
    
    args_list = [(uid,num_images,valid_uids) for uid in obj_paths]
    

    obj_uids = []

    for _ in tqdm(pool.imap_unordered(process_uid, args_list), total=len(args_list)):
        if _ is not None:
            obj_uids += _



    random.shuffle(obj_uids)
    n = len(obj_uids)
    train_nums = int(train_ratio * n)
    train_uids = obj_uids[:train_nums]
    test_uids = obj_uids[train_nums:]
    print('objects in train:',len(train_uids))
    print('objects in test:',len(test_uids))

    train_json_path = os.path.join('/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture','train_meta.json')
    test_json_path = os.path.join('/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture','test_meta.json')

    # 将列表写入JSON文件
    with open(train_json_path, 'w') as json_file:
        json.dump(train_uids, json_file)

    with open(test_json_path, 'w') as json_file:
            json.dump(test_uids, json_file)
    
def process_uid(args):
    x,num_images,valid_uids = args
    if not os.path.isdir(x):
        return None

    if valid_uids is None:
        valid_uids = []
    uid = os.path.basename(x)
    # paths = glob.glob(os.path.join(x,'*'))
    paths = [x]

    results = []
    for i in range(len(paths)):
        path = paths[i]
        if os.path.isdir(path):

            rgba_files = glob.glob(path + '/image/*')
            depth_files = glob.glob(path + '/depth_png/*')
            normal_files = glob.glob(path + '/normal/*')

            condition1 =  (len(rgba_files) == num_images) and (len(depth_files) >= num_images) and (len(normal_files) >= num_images)






            if condition1:
            # if condition1:
                

                if len(valid_uids)>0:
                    if uid in valid_uids:
                        results.append(path)
                    else:
                        print(uid,' is not in valid uids')
                else:
                        results.append(path)



            else:
                print(f"=========warining==========")
                print(f"wrong renders of {path}")
                continue
    return results

if __name__ == "__main__":
    
    root_dir = '/home/admin/data_meta_info.txt'
    calculate_score('/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture')
    # get_high_score_paths('/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture/color_texutre_scores.json')
    vis_datasets('/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture',num_object=100,num_of_views=1,output_path='/mnt/xlab-nas-2/shaomingqi.smq/projects/aigc3d_dev/aigc3d/data_process/3d-expand/high_quality_texture/vis.png')
 