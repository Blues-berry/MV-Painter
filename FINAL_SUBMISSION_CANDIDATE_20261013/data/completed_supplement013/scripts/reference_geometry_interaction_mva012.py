"""Layout adapter for the frozen factorial candidate on six-view CFG batches."""
import torch
from reference_geometry_interaction012 import correct_interaction

def correct_multiview_interaction(full, bare, guidance_scale, num_views=6):
    if full.shape != bare.shape or full.ndim != 4 or full.shape[0] != 2*num_views:
        raise ValueError('Expected exactly one object: negative views then positive views')
    _,channels,height,width=full.shape
    def pack(x):return x.reshape(2,num_views,channels,height,width).permute(0,2,1,3,4).reshape(2,channels,num_views*height,width)
    changed,parts=correct_interaction(pack(full),pack(bare),guidance_scale)
    result=changed.reshape(2,channels,num_views,height,width).permute(0,2,1,3,4).reshape_as(full)
    return result,parts
