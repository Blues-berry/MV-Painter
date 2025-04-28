import os
import json
import cv2
import numpy as np
import random
import webdataset as wds
import pytorch_lightning as pl
import torch
from torch.utils.data import Dataset
from torch.utils.data.distributed import DistributedSampler
from PIL import Image
from pathlib import Path
from src.utils.train_util import instantiate_from_config
from torchvision.utils import save_image
import torch.nn.functional as F
import torchvision
class DataModuleFromConfig(pl.LightningDataModule):
    def __init__(
            self,
            batch_size=8,
            num_workers=4,
            train=None,
            validation=None,
            test=None,
            **kwargs,
    ):
        super().__init__()

        self.batch_size = batch_size
        self.num_workers = num_workers

        self.dataset_configs = dict()
        if train is not None:
            self.dataset_configs['train'] = train
        if validation is not None:
            self.dataset_configs['validation'] = validation
        if test is not None:
            self.dataset_configs['test'] = test

    def setup(self, stage):

        if stage in ['fit']:
            # for k in self.dataset_configs:
            #     print(k)
            #     print(self.dataset_configs[k])
            # print(self.dataset_configs)
            # self.datasets = {"train":instantiate_from_config(self.dataset_configs["train"])}
            self.datasets = dict((k, instantiate_from_config(self.dataset_configs[k])) for k in self.dataset_configs)
        else:
            raise NotImplementedError

    def train_dataloader(self):

        sampler = DistributedSampler(self.datasets['train'])
        return wds.WebLoader(self.datasets['train'], batch_size=self.batch_size, num_workers=self.num_workers,
                             shuffle=False, sampler=sampler)

    def val_dataloader(self):

        sampler = DistributedSampler(self.datasets['validation'])
        return wds.WebLoader(self.datasets['validation'], batch_size=4, num_workers=self.num_workers, shuffle=False,
                             sampler=sampler)

    def test_dataloader(self):

        return wds.WebLoader(self.datasets['test'], batch_size=self.batch_size, num_workers=self.num_workers,
                             shuffle=False)


class MVPainterData(Dataset):
    def __init__(self,
                 root_dir_list=['objaverse/'],
                 meta_fname='valid',
                 valid_path = None
                 ):
        all_paths = []
        if valid_path is not None:
            with open(valid_path,'r') as f:
                data = f.readlines()
                for line in data:
                    line = line.strip().replace("NaN", "-1")
                    meta = eval(line)
                    mesh_path = meta['img_2501'].replace('workspace','xlab-nas-2').replace('\n','').replace('\r','').split('/')[:-1]
                    mesh_path = '/'.join(mesh_path)
                    all_paths.append(mesh_path)

        else:
            self.root_dir_list = root_dir_list
            for root_dir in root_dir_list:
                paths = os.listdir(root_dir)
                paths = [os.path.join(root_dir,path) for path in paths]
                all_paths = all_paths + paths
                

        if "train" in meta_fname:
            self.paths = all_paths[:-20]
        else:
            self.paths = all_paths[-20:]

        self.target_order = [0,15,12,7,13,14]

        total_objects = len(self.paths)
        self.random_ratio_range=0.8
        print('============= length of dataset %d =============' % len(self.paths))

    def __len__(self):
        return len(self.paths)
    def random_resize(self,img,random_ratio=0.8):
        bg_color=img[0,0,:]
        img_new=np.ones_like(img)*bg_color
        h,w,_=img.shape


        h_new = int(h * random_ratio)
        w_new = int(w * random_ratio)
        h_offset=int((h-h_new)/2)
        w_offset=int((w-w_new)/2)
        img_resized = cv2.resize(img, (w_new, h_new))
        # print(img_resized.shape)
        img_new[h_offset:h_offset+h_new, w_offset:w_offset+w_new] = img_resized
        return img_new
    
    def random_stretch_or_compress(self,image, min_scale=0.5, max_scale=1.5):
        assert image.shape[2] == 4
    
        # 获取原始图像的尺寸
        h, w = image.shape[:2]
        
        # 找到mask区域的边界
        mask = image[:, :, 3] != 0
        mask = mask.astype(np.uint8)

        x, y, w_mask, h_mask = cv2.boundingRect(mask)
        
        # 随机选择缩放比例
        scale_width = random.uniform(min_scale, max_scale)
        scale_height =random.uniform(min_scale, max_scale)
        
        # 提取mask区域
        mask_region = image[y:y+h_mask, x:x+w_mask]
        
        # 计算缩放后的新尺寸
        new_width = int(w_mask * scale_width)
        new_height = int(h_mask * scale_height)
        
        # 保证新的尺寸不会超出原图范围
        new_width = min(new_width, w - x)
        new_height = min(new_height, h - y)
        
        # 拉伸或压缩mask区域
        resized_region = cv2.resize(mask_region, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # 创建一个新的空白图像来放置结果
        result_image = image.copy() * 0

        # 计算原始区域的中心点
        original_center_x = x + w_mask // 2
        original_center_y = y + h_mask // 2

        # 计算缩放后区域的中心点
        new_center_x = original_center_x
        new_center_y = original_center_y
        
        # 计算新的mask区域的起始位置，确保它的中心点保持一致
        new_x = new_center_x - new_width // 2
        new_y = new_center_y - new_height // 2
        
        # 确保新的区域不会超出图像范围
        new_x = max(new_x, 0)
        new_y = max(new_y, 0)
        # 将拉伸后的区域放回原图中的mask区域
        result_image[new_y:new_y+new_height, new_x:new_x+new_width] = resized_region
        
        return result_image

    def load_im_cond(self, path, color, random_ratio=0.8):
        cond_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        # alpha_channel = cond_img[:, :, 3]
        # cond_img = cond_img[:, :, :3]
        cond_img = cv2.cvtColor(cond_img, cv2.COLOR_BGRA2RGBA)


        # 去除cond image的增强
        cond_img = self.random_stretch_or_compress(cond_img)
        cond_img = self.random_resize(cond_img,random_ratio)

       

        image = np.asarray(cond_img, dtype=np.float32) / 255.
        if image.shape[2] == 3:
            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            return image, None
        else:
            alpha = image[:, :, 3:]
            image = image[:, :, :3] * alpha + color * (1 - alpha)

            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            alpha = torch.from_numpy(alpha).permute(2, 0, 1).contiguous().float()
            return image, alpha

    
    def load_ccm_position_im(self,path,color,random_ratio = 0.9):
        img=cv2.imread(path,cv2.IMREAD_UNCHANGED)
        img=cv2.cvtColor(img,cv2.COLOR_BGRA2RGBA)
        # img = (255 - img) * 2

        # img = self.expand_img_from_07_98(img)
        # img=self.random_resize(img,random_ratio)
        # img = cv2.resize(img,(512,512))
        # image=img/ 255.
        
        image = img / 255.
        # pil_img = Image.open(path)
        #
        # image = np.asarray(pil_img, dtype=np.float32) / 255.
        if len(image.shape) == 2:
            image = np.array([image, image, image], axis=0)
            image = torch.from_numpy(image).contiguous().float()
            return image, None
        elif image.shape[2] == 3:
            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            return image, None
        else:
            alpha = image[:, :, 3:]
            image = image[:, :, :3] * alpha + color * (1 - alpha)

            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            alpha = torch.from_numpy(alpha).permute(2, 0, 1).contiguous().float()
            return image, alpha
    
    def load_im(self, path, color, random_ratio=0.8):
        img=cv2.imread(path,cv2.IMREAD_UNCHANGED)
        img=cv2.cvtColor(img,cv2.COLOR_BGRA2RGBA)
        # img = self.expand_img_from_07_98(img)
        # img=self.random_resize(img,random_ratio)
        # img = cv2.resize(img,(512,512))
        # image=img/ 255.
        image = img / 255.
        # pil_img = Image.open(path)
        #
        # image = np.asarray(pil_img, dtype=np.float32) / 255.
        if len(image.shape) == 2:
            image = np.array([image, image, image], axis=0)
            image = torch.from_numpy(image).contiguous().float()
            return image, None
        elif image.shape[2] == 3:
            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            return image, None
        else:
            alpha = image[:, :, 3:]
            image = image[:, :, :3] * alpha + color * (1 - alpha)

            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            alpha = torch.from_numpy(alpha).permute(2, 0, 1).contiguous().float()
            return image, alpha
    

    def expand_img_from_07_98(self,img,ratio = 0.98 / 0.7):
        # 获取原始图像的尺寸
        h, w = img.shape[:2]
        
        # 计算新的尺寸
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        
        # 计算中心点
        center_x, center_y = w // 2, h // 2
        # print(111)
        # img_pillow = Image.fromarray(img)
        # resized_img_pillow = img_pillow.resize((new_w, new_h), resample=Image.LANCZOS)
        # # 计算放大后的图像
        resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        # resized_img = np.array(resized_img_pillow)

        # 计算裁剪区域的起始点
        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2
        
        # 提取放大后中心区域
        cropped_img = resized_img[start_y:start_y + h, start_x:start_x + w]
        
        return cropped_img
        
        

    def load_im_normal(self, path, color, random_ratio=0.8):
        img=cv2.imread(path,cv2.IMREAD_UNCHANGED)
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # img = self.expand_img_from_07_98(img)

        # img=self.random_resize(img,random_ratio)
        # img = cv2.resize(img,(512,512))
        # image=img/ 255.
        image = img / 65535.
        # pil_img = Image.open(path)
        #
        # image = np.asarray(pil_img, dtype=np.float32) / 255.
        if len(image.shape) == 2:
            image = np.array([image, image, image], axis=0)
            image = torch.from_numpy(image).contiguous().float()
            return image, None
        elif image.shape[2] == 3:
            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            return image, None
        else:
            alpha = image[:, :, 3:]
            image = image[:, :, :3] * alpha + color * (1 - alpha)

            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            alpha = torch.from_numpy(alpha).permute(2, 0, 1).contiguous().float()
            return image, alpha


    def load_img_depth(self,path,color,random_ratio=0.8):
        img=cv2.imread(path,cv2.IMREAD_UNCHANGED)
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        
        # img = self.expand_img_from_07_98(img)

        # img=self.random_resize(img,random_ratio)
        # img = cv2.resize(img,(512,512))
        # image=img/ 255.
        image = img / 65535.
        # pil_img = Image.open(path)
        #
        # image = np.asarray(pil_img, dtype=np.float32) / 255.
        if len(image.shape) == 2:
            image = np.array([image, image, image], axis=0)
            image = torch.from_numpy(image).contiguous().float()
            return image, None
        elif image.shape[2] == 3:
            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            return image, None
        else:
            alpha = image[:, :, 3:]
            image = image[:, :, :3] * alpha + color * (1 - alpha)

            image = torch.from_numpy(image).permute(2, 0, 1).contiguous().float()
            alpha = torch.from_numpy(alpha).permute(2, 0, 1).contiguous().float()
            return image, 
            
        
    def blur_tensors(self, tensors, scale=0.5):
        """
        模糊操作：先将图像缩放，再缩放回来
        :param tensors: Tensor，形状为(6, 3, h, w)
        :param scale: 缩放因子
        :return: 模糊后的Tensor
        """
        # 先缩放到 (6, 3, h*scale, w*scale)
        batch_size, channels, h, w = tensors.shape
        new_h, new_w = int(h * scale), int(w * scale)
        scaled_tensors = F.interpolate(tensors, size=(new_h, new_w), mode='bilinear', align_corners=False)

        # 再缩放回来到原始大小
        blurred_tensors = F.interpolate(scaled_tensors, size=(h, w), mode='bilinear', align_corners=False)

        return blurred_tensors
    def rotate_normal_z_90(self,tensor):
        """
        将包含 normal 信息的张量绕 z 轴旋转 90 度
        :param tensor: shape 为 (c, h, w)，其中 c = 3，表示 (x, y, z) 的 normal 信息
        :return: 旋转后的张量
        """
        # 检查输入张量是否满足要求
        if tensor.shape[0] != 3:
            raise ValueError("输入张量的第一个维度必须是 3，表示 (x, y, z) 的 normal 信息")
        tensor = (tensor - 0.5) *2
        # 定义旋转矩阵 Rz(90°)
        Rz = torch.tensor([
            [0, -1, 0],
            [1,  0, 0],
            [0,  0, 1]
        ], dtype=tensor.dtype, device=tensor.device)  # 确保数据类型和设备与输入张量一致

        # 将张量展平为 (3, h*w)，以便进行矩阵乘法
        h, w = tensor.shape[1], tensor.shape[2]
        tensor_flat = tensor.view(3, -1)  # shape: (3, h*w)

        # 应用旋转矩阵
        rotated_flat = torch.matmul(Rz, tensor_flat)  # shape: (3, h*w)

        # 将张量恢复原始形状
        rotated_tensor = rotated_flat.view(3, h, w)  # shape: (3, h, w)
        rotated_tensor = (rotated_tensor + 1) / 2

        return rotated_tensor


    def __getitem__(self, index):

        # self.paths = os.listdir(self.root_dir)[:-20]
        # self.__len__()
        item_random_ratio = random.uniform(self.random_ratio_range, 1)
        while True:
            pbr_image_path = os.path.join(self.paths[index], 'image')
            normal_image_path = os.path.join(self.paths[index], 'normal')
            depth_image_path = os.path.join(self.paths[index], 'depth_png')


            base_dir_name = self.paths[index].split('/')[:-2]
            object_uid = self.paths[index].split('/')[-1]
            print('base dir name:',base_dir_name)

            while not (os.path.exists(pbr_image_path) and os.path.exists(normal_image_path) ):
                index = random.randint(0, len(self.paths))
                pbr_image_path = os.path.join(self.paths[index], 'image')
                normal_image_path = os.path.join(self.paths[index], 'normal')
                depth_image_path = os.path.join(self.paths[index], 'depth_png')

                base_dir_name = self.paths[index].split('/')[:-2]
                object_uid = self.paths[index].split('/')[-1]
                print('base dir name:',base_dir_name)

            '''background color, default: white'''
            bkg_color = [1., 1., 1.]


            normal_img_list = []
            res_img_list = []
            depth_img_list = []


            try:
                first_image,first_alpha = self.load_im(os.path.join(pbr_image_path, '000.png'), bkg_color, item_random_ratio)
                fourth_image,fourth_alpha = self.load_im(os.path.join(pbr_image_path, '014.png'), bkg_color, item_random_ratio)
                first_alpha_count = torch.sum(first_alpha==0).item()
                fourth_alpha_count = torch.sum(fourth_alpha==0).item()
                print("alpha count:",first_alpha_count,fourth_alpha_count)
                if first_alpha_count > fourth_alpha_count:
                    # 第一视角是侧面图，顺序进行反转
                    reverse = True
                    print("reverse true")
                else:
                    reverse = False
                    print("reverse false")

                
                if reverse:
                    cond_img_name = '014.png'
                    current_target_order = [14,15,0,15,12,13]

                else:
                    cond_img_name = '000.png'
                    current_target_order = [0,15,12,15,13,14]

    
 
                cond_img, alpha = self.load_im_cond(
                    os.path.join(pbr_image_path, cond_img_name),
                    bkg_color, item_random_ratio
                )
                for idx in current_target_order:

                    img, alpha = self.load_im(os.path.join(pbr_image_path, '%03d.png' % idx), bkg_color,item_random_ratio)
                    res_img_list.append(img)

                    depth_img, alpha = self.load_img_depth(os.path.join(depth_image_path, '%03d.png' % idx), bkg_color,item_random_ratio)
                    depth_img_list.append(depth_img)


     

                    img, alpha = self.load_im_normal(os.path.join(normal_image_path, '%03d.png' % idx), bkg_color,item_random_ratio)
                    # normal进行坐标系旋转
                    if reverse:
                        img = self.rotate_normal_z_90(img)
            
                    normal_img_list.append(img)



                if reverse:
                    res_img_list[1] = torchvision.transforms.functional.rotate(res_img_list[1],angle=90)
                    res_img_list[3] = torchvision.transforms.functional.rotate(res_img_list[3],angle=90)
                    normal_img_list[1] = torchvision.transforms.functional.rotate(normal_img_list[1],angle=90)
                    normal_img_list[3] = torchvision.transforms.functional.rotate(normal_img_list[3],angle=90)
                    depth_img_list[1] = torchvision.transforms.functional.rotate(depth_img_list[1],angle=90)
                    depth_img_list[3] = torchvision.transforms.functional.rotate(depth_img_list[3],angle=90)
                

        
                # 对depth进行归一化
                depth_imgs = torch.stack(depth_img_list, dim=0).float()

                valid_mask = depth_imgs < 1.0

                depth_imgs[valid_mask] = 1 / depth_imgs[valid_mask]

                min_depth = torch.min(depth_imgs[valid_mask])
                max_depth = torch.max(depth_imgs[valid_mask])
                depth_imgs[valid_mask] = (depth_imgs[valid_mask] - min_depth) / (max_depth - min_depth) # (6,3,512,512)
                                        
                                

            except Exception as e:
                print(e)
                print("wrong path:",pbr_image_path)
                
                index = random.randint(0, len(self.paths))
                continue
            break





        normal_imgs = torch.stack(normal_img_list, dim=0).float()




        # # 随机对control信号模糊处理
        # if random.uniform(0, 1) < 0.2:
        #     blur_ratio = random.uniform(0.2,0.5)
           
        #     normal_imgs = self.blur_tensors(normal_imgs,blur_ratio)

            


        data = {
            'cond_imgs': cond_img,  # (3, H, W)
            'target_imgs': torch.stack(res_img_list, dim=0).float(),  # (6, 3, H, W)
            'depth_imgs': normal_imgs,
            'real_depth_imgs':depth_imgs,
            # 'target_ccm_position_imgs': torch.stack(ccm_position_img_list, dim=0).float(),  # (6, 3, H, W)

        }
        return data

if __name__ == '__main__':
    dataset = ObjaverseData(root_dir=r'/home/sunzhaoxu/mingqi.smq')
    img=cv2.imread(r"/home/sunzhaoxu/mingqi.smq/000.png",cv2.IMREAD_UNCHANGED)
    img=cv2.cvtColor(img,cv2.COLOR_BGRA2RGBA)
    img=dataset.random_stretch_or_compress(img,0.5,2.0)
    img=cv2.cvtColor(img,cv2.COLOR_BGRA2RGBA)

    cv2.imwrite("test.png",img)
    cv2.imwrite("test_mask.png",img[:,:,-1])