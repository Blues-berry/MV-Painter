import numpy as np
import cv2
import torch
import math
from kornia.losses import ssim_loss
from utils.misc import rgb_to_srgb as _tonemap_srgb
from utils.misc import srgb_to_rgb
from lpips import LPIPS


def mse_to_psnr(mse):
    """Compute PSNR given an MSE (we assume the maximum pixel value is 1)."""
    return -10. / np.log(10.) * np.log(mse)


def calc_PSNR(img_pred, img_gt, mask_gt,
              max_value, use_gt_median, tonemapping, scale_invariant,
              divide_mask=True):
    '''
    calculate the PSNR between the predicted image and ground truth image.
    a scale is optimized to get best possible PSNR.
    images are clip by max_value_ratio.
    Args:
        img_pred: numpy.ndarray of shape [B, SH, W, 3]. predicted HDR image.
        img_gt: numpy.ndarray of shape [B, H, W, 3]. ground truth HDR image.
        mask_gt: numpy.ndarray of shape [B, H, W, 1]. ground truth foreground mask.
        max_value: Float. the maximum value of the ground truth image clipped to.
            This is designed to prevent the result being affected by too bright pixels.
        tonemapping: Bool. Whether the images are tone-mapped before comparion.
        divide_mask: Bool. Whether the mse is divided by the foreground area.
    '''

    img_pred = img_pred * mask_gt
    img_gt = img_gt * mask_gt
    img_gt[img_gt < 0] = 0
    if use_gt_median:  # image in linear space are usually too dark, need to re-normalize
        if img_gt.clip(0, 1).mean() > 1e-8:
            gt_median = _tonemap_srgb(img_gt.clip(0, 1)).mean() / img_gt.clip(0, 1).mean()
            img_pred = img_pred * gt_median
            img_gt = img_gt * gt_median

    if scale_invariant:
        scale = (img_gt * img_pred).sum(axis=(1, 2, 3)) / (img_pred ** 2).sum(axis=(1, 2, 3))
        scale = scale[..., None, None, None]
        # scale = (img_gt * img_pred).sum(axis=(1, 2)) / (img_pred ** 2).sum(axis=(1, 2))
        # scale = scale[:, None, None, :]
        img_pred = scale * img_pred

    # clip the prediction and the gt img by the maximum_value
    # XXX: order of clip and scale ???
    img_pred = np.clip(img_pred, 0, max_value)
    img_gt = np.clip(img_gt, 0, max_value)

    if tonemapping:
        img_pred = _tonemap_srgb(img_pred)
        img_gt = _tonemap_srgb(img_gt)

    if not divide_mask:
        mse = ((img_pred - img_gt) ** 2).mean(axis=(1, 2, 3))
        lb = ((np.ones_like(img_gt) * .5 * mask_gt - img_gt) ** 2).mean(axis=(1, 2, 3))
    else:
        mask_gt = np.repeat(mask_gt, 3, axis=-1)
        # XXX: mask only has one channel. mask.sum() * 3 !!! Check ORB code!!!
        mse = ((img_pred - img_gt) ** 2).sum(axis=(1, 2, 3)) / mask_gt.sum(axis=(1, 2, 3)) 
        lb = ((np.ones_like(img_gt) * .5 * mask_gt - img_gt) ** 2).sum(axis=(1, 2, 3)) / mask_gt.sum(axis=(1, 2, 3))
    out = mse_to_psnr(mse)
    lb = mse_to_psnr(lb)
    out = np.maximum(out, lb)
    return out


def ssim(inputs, target, mask, device='cuda'):
    """
    SSIM metric

    Args: numpy.ndarray
    """
    if ssim_loss is None:
        return np.nan

    inputs = inputs * mask
    target = target * mask

    # image_pred and image_gt: (B, 3, H, W) in range [0, 1]
    inputs = torch.tensor(inputs, dtype=torch.float32, device=device).permute(0, 3, 1, 2)
    target = torch.tensor(target, dtype=torch.float32, device=device).permute(0, 3, 1, 2)
    # dssim_ = ssim_loss(inputs, target, 3).item()  # dissimilarity in [0, 1]
    dssim_ = ssim_loss(inputs, target, 3, reduction='none').mean(dim=(1, 2, 3)).cpu().numpy()
    return 1 - 2 * dssim_  # in [-1, 1]


def mse(inputs, target, mask, root=False):
    if inputs.shape[-1] != mask.shape[-1]:
        mask = np.repeat(mask, inputs.shape[-1], axis=-1)
    error = (inputs - target) ** 2 * mask
    error = error.sum(axis=(1, 2, 3)) / mask.sum(axis=(1, 2, 3))
    # error = error.mean(axis=(1, 2, 3)) # XXX
    if root:
        error = np.sqrt(error)
    return error


def simse(img_pred, img_gt, mask_gt, divide_mask=False):
    if img_gt.shape[-1] != mask_gt.shape[-1]:
        mask_gt = np.repeat(mask_gt, img_gt.shape[-1], axis=-1)

    img_pred = img_pred * mask_gt
    img_gt = img_gt * mask_gt
    img_gt[img_gt < 0] = 0

    scale = (img_gt * img_pred).sum(axis=(1, 2, 3)) / (img_pred ** 2).sum(axis=(1, 2, 3))
    scale = scale[..., None, None, None]
    img_pred = scale * img_pred

    if divide_mask:
        mse = ((img_pred - img_gt) ** 2).sum(axis=(1, 2, 3)) / mask_gt.sum(axis=(1, 2, 3))
    else:
        mse = ((img_pred - img_gt) ** 2).mean(axis=(1, 2, 3))
    return mse


def calc_lpips(inputs: np.ndarray, target: np.ndarray, mask: np.ndarray, lpips, device='cuda'):
    inputs = inputs * mask
    target = target * mask

    inputs = torch.tensor(inputs, dtype=torch.float32, device='cuda').permute(0, 3, 1, 2)
    target = torch.tensor(target, dtype=torch.float32, device='cuda').permute(0, 3, 1, 2)
    loss = lpips(inputs, target, normalize=True) # normalized to [-1,1]
    loss = loss.flatten().detach().cpu().numpy()
    return loss


def erode_mask(mask):
    # shrink mask by a small margin to prevent inaccurate mask boundary.
    if mask.shape[-1] == 3:
        mask = mask[..., 0]
    if mask.dtype == np.float32:
        mask = (mask*255).clip(0, 255).astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    out_mask = []
    for m in mask:
        m = cv2.erode(m, kernel)
        out_mask.append(m)
    out_mask = np.stack(out_mask, axis=0)
    out_mask = (out_mask > 127).astype(np.float32)
    # return (mask > 127).astype(np.float32)
    return out_mask


class MetricCalculator:
    r"""
    Metric calculator
    """

    def __init__(self, metrics, device):
        self.metrics = metrics
        self.lpips = None
        self.device =device


    def compute_albedo(self, albedo_pred, albedo_gt, mask_gt, metrics):
        """
        Metrics for albedo estimation: SSIM, PSNR(scale-invariant)
        Args:
            albedo_pred (numpy.ndarray): [B, H, W, 3]
        """
        assert albedo_pred.shape == albedo_gt.shape, (albedo_pred.shape, albedo_gt.shape)

        ret = {}

        for metric in metrics:
            if metric == 'ssim':
                ret['albedo-ssim'] = ssim(albedo_pred, albedo_gt, mask_gt, device=self.device)
            elif metric == 'psnr':
                ret['albedo-psnr'] = calc_PSNR(
                    albedo_pred,
                    albedo_gt,
                    mask_gt,
                    max_value=1.0,
                    use_gt_median=False,
                    tonemapping=False,
                    scale_invariant=True,
                    divide_mask=False,
                )
            elif metric == 'mse':
                ret['albedo-mse'] = mse(albedo_pred, albedo_gt, mask_gt)
            elif metric == 'rmse':
                ret['albedo-rmse'] = mse(albedo_pred, albedo_gt, mask_gt, root=True)
            elif metric == 'simse':
                ret['albedo-simse-mask'] = simse(albedo_pred, albedo_gt, mask_gt, divide_mask=True)
                ret['albedo-simse-meam'] = simse(albedo_pred, albedo_gt, mask_gt, divide_mask=False)
            elif metric == 'lpips':
                if self.lpips is None:
                    self.lpips = LPIPS(net='vgg', verbose=False).to(self.device)
                ret['albedo-lpips'] = calc_lpips(albedo_pred, albedo_gt, mask_gt, self.lpips, device=self.device)
            else:
                raise NotImplementedError(f"Unsupported metric for albedo: {metric}")

        return ret


    def compute_material(self, mr_pred, mr_gt, mask_gt, metrics):
        """
        Metrics for roughness and metallic estimation: L1 loss
        Args:
            mr_pred (numpy.ndarray): [B, H, W, 2]
            mr_gt (numpy.ndarray): [B, H, W, 2]
            mask_gt (numpy.ndarray): [B, H, W, 1]
        """
        assert mr_pred.shape == mr_gt.shape, (mr_pred.shape, mr_gt.shape)

        m_gt, r_gt = mr_gt[..., :1], mr_gt[..., 1:]
        metallic, roughness = mr_pred[..., :1], mr_pred[..., 1:]

        ret = {}
        for metric in metrics:
            if metric == 'mse':
                ret['roughness_mse'] = mse(roughness, r_gt, mask_gt)
                ret['metallic_mse'] = mse(metallic, m_gt, mask_gt)
            elif metric == 'rmse':
                ret['roughness_rmse'] = mse(roughness, r_gt, mask_gt, root=True)
                ret['metallic_rmse'] = mse(metallic, m_gt, mask_gt, root=True)
            else:
                raise NotImplementedError(f"Unsupported metric for material: {metric}")
        return ret


    def compute_normal(self, normal_pred, normal_gt, mask_gt, metrics):
        '''
        Metrics for normal estimation: cosine distance and DIA(deviation in angle)

        Args:
            normal_pred (numpy.ndarray): [B, H, W, 3]
            normal_gt (numpy.ndarray): [B, H, W, 3]
            mask_gt (numpy.ndarray): [B, H, W, 1]
        '''
        assert normal_pred.shape == normal_gt.shape, (normal_pred.shape, normal_gt.shape)

        eps = 1e-6
        normal_pred = normal_pred / (np.linalg.norm(normal_pred, axis=-1, keepdims=True) + eps)
        normal_gt = normal_gt / (np.linalg.norm(normal_gt, axis=-1, keepdims=True) + eps)
        mask_gt = mask_gt.squeeze(-1)

        cos_similar = (normal_pred * normal_gt).sum(axis=-1)
        ret = {}
        for metric in metrics:
            if metric == 'cosine_similarity':
                cosine_similarity = cos_similar * mask_gt
                ret['normal-cosine_similarity'] = cosine_similarity.sum(axis=(1, 2)) / mask_gt.sum(axis=(1, 2))
            elif metric == 'cosine_distance':
                cosine_distance = (1 - cos_similar) * mask_gt
                ret['normal-cosine_distance'] = cosine_distance.sum(axis=(1, 2)) / mask_gt.sum(axis=(1, 2))
            elif metric == 'dia':
                dia = (np.arccos(cos_similar.clip(-1, 1)) / math.pi * 180) * mask_gt
                ret['normal-dia'] = dia.sum(axis=(1, 2)) / mask_gt.sum(axis=(1, 2))
            else:
                raise NotImplementedError(f"Unsupported metric for normal: {metric}")

        return ret


    def __call__(self, img_pred, img_gt, mask):
        img_pred = img_pred.detach().cpu().numpy()
        img_gt = img_gt.detach().cpu().numpy()
        mask = mask.detach().cpu().numpy()

        albedo_gt = img_gt[::3]
        normal_gt = img_gt[1::3]
        mr_gt = img_gt[2::3,:2]
        albedo_pred = img_pred[::3]
        normal_pred = img_pred[1::3]
        mr_pred = img_pred[2::3,:2]

        mask = mask.transpose(0, 2, 3, 1)
        # mask = erode_mask(mask)[..., None]
        albedo_gt, albedo_pred = albedo_gt.transpose(0, 2, 3, 1), albedo_pred.transpose(0, 2, 3, 1)
        # albedo_pred = srgb_to_rgb(albedo_pred)
        # albedo_gt = srgb_to_rgb(albedo_gt)

        ret = {}
        ret.update(self.compute_albedo(albedo_pred, albedo_gt, mask, self.metrics['albedo']))
        if normal_pred is not None:
            normal_gt, normal_pred = normal_gt.transpose(0, 2, 3, 1), normal_pred.transpose(0, 2, 3, 1)
            normal_gt, normal_pred = 2 * normal_gt - 1, 2 * normal_pred - 1 # to [-1, 1]
            ret.update(self.compute_normal(normal_pred, normal_gt, mask, self.metrics['normal']))
        if mr_pred is not None:
            mr_gt, mr_pred = mr_gt.transpose(0, 2, 3, 1), mr_pred.transpose(0, 2, 3, 1)
            ret.update(self.compute_material(mr_pred, mr_gt, mask, self.metrics['material']))
        return ret
