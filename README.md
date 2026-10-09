# MVPainter
<div align="left">
  <a href=https://amap-cvlab.github.io/MV-Painter/ target="_blank"><img src=https://img.shields.io/badge/Project%20Page-333399.svg?logo=homepage height=22px></a>
 <a href='https://huggingface.co/shaomq/MVPainter'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Model-blue'></a> &nbsp;
 <a href='https://arxiv.org/pdf/2505.12635'><img src='https://img.shields.io/badge/arXiv-Report-b31b1b.svg'></a> &nbsp;

</div>
MVPainter is a fully open-source system for 3D texture generation, providing a comprehensive solution including data, models, and evaluation tools.

<img src="./assets/teaser.png" alt="Pipeline" width="800"/>


- [ ] Release gradio demo.
- [x] Release technical report.
- [x] Release training code.
- [x] Release data processing code.

## ✨Key Features
* 🔓 Fully Open-Source Texture Generation Pipeline

* 🧩 Compatible with Mainstream 3D Geometry Generation Methods

* 🎨 High-Fidelity, Geometry- and Image-Aligned PBR Texture Generation


## 🔥 News
* [2025-04-30] We have released our [technical report](https://huggingface.co/shaomq/MVPainter)!
* [2025-04-30] We have released model weights, data processing, trainning, inference scripts.

## 🔧[Installation](./MVPainter/INSTALL.md)
Installation guides can be found in [INSTALL.md](./MVPainter/INSTALL.md).

## 💡Infererence
### Generate multi-view images

1. Prepare the input images and glbs in `/data/test/imgs` and `/data/test/glbs`.

2. Run the following command to infer:
    ```
    python infer_multiview.py --input_glb_dir ./data/test/glbs --input_img_dir ./data/test/imgs --output_dir ./outputs/test --geo_rotation 0
    ```




    Mesh generated from [TripoSG](https://github.com/VAST-AI-Research/TripoSG), use `--geo_rotation 0`

    Mesh generated from [Hunyuan-2](https://github.com/Tencent/Hunyuan3D-2), use `--geo_rotation -90`

    Mesh generated from [TRELLIS](https://github.com/microsoft/TRELLIS)，use  `--geo_rotation -90`

    Mesh generated from [Hi3dGen](https://github.com/Stable-X/Hi3DGen)  `--geo_rotation -90`


### Extract PBR (Optional)
Extract PBR attributes from generated mul-view images.

```
python infer_pbr.py --mv_res_dir ./outputs/test
```

The extracted PBR maps will be saved in `--mv_res_dir` directory.



### Painting

Run the following command to paint 3d model with multi-view generations:

```
python infer_paint.py --mv_res_dir ./outputs/test/mvpainter --output_dir ./results/test/mvpainter
```
If use PBR:
```
python infer_paint.py --mv_res_dir ./outputs/test/mvpainter --output_dir ./results/test/mvpainter --use_pbr
```

`--mv_res_dir` is the directory of the generated multi-view images.



## 🏋️Training
### Multi-View Generation Model
#### Train UNet
```
python train.py --base=./configs/mvpainter-train-unet.yaml --gpus 0 --num_nodes 32 --logdir=./logs
```

#### Train controlnet
```
python train.py --base=./configs/mvpainter-train-controlnet.yaml --gpus 0 --num_nodes 32 --logdir=./logs
```

### PBR Model
Our pbr model is improved based on [IDArb](https://github.com/Lizb6626/IDArb). The specific improvements can be found in our technical report. Our training script is similar to IDArb:

```
accelerate launch --config_file configs/acc/8gpu.yaml train_pbr.py --config configs/train.yaml

```
## 📊[Data Processing](./data_process/README.md)
Dataprocess guides can be found in [here](./data_process/README.md)

## 📝[Evaluation](./MVPainter/evaluation/README.md)
Our human-aligned evaluation system can be found in [here](./MVPainter/evaluation/README.md)

## Citation
If you found this repository helpful, please cite our report:

```
@article{shao2025mvpainter,
  title={MVPainter: Accurate and Detailed 3D Texture Generation via Multi-View Diffusion with Geometric Control},
  author={Shao, Mingqi and Xiong, Feng and Sun, Zhaoxu and Xu, Mu},
  journal={arXiv preprint arXiv:2505.12635},
  year={2025},
  url={https://arxiv.org/abs/2505.12635}
}
```
## ⭐️Acknowledgment

In this project we use parts of the implementations of the following works:
- [Hunyuan3D-1](https://github.com/Tencent/Hunyuan3D-1)
- [Hunyuan3D-2](https://github.com/Tencent/Hunyuan3D-2)
- [IDArb](https://github.com/Lizb6626/IDArb)
- [MaterialAnything](https://github.com/3DTopia/MaterialAnything)


We thank these work's contributors for open sourcing their research and exploration.

## Current C&G revision workspace

The active second-round manuscript is based on the authenticated 2026-09-07 01549 submission. Its immutable source is `1008/manuscript/source_01549/final_0903.tex` (SHA-256 `203966151e1129d308b7827ececab194d2abf12c2e2639249444d11d09320a01`). The current manuscript, Supplement, reviewer response, source package, PDFs, figure provenance, and revision integrity log are under `1008/`.

Build the manuscript and Supplement from `1008/manuscript/revision_01549_restored/` with `build_revision_1008.sh` and `build_supplement_1008.sh`. Build the addition-marked comparison with `build_marked_up_1008.sh`. The author-review copies are in `1008/submission_1008_author_review/` and are regenerated from those active sources. Raw experiment outputs and identity-linked participant data remain outside the tracked paper package; small reports and summary evidence are indexed under `1009/`.

<!-- ## Star History

[![Star History](https://api.star-history.com/svg?repos=amap-cvlab/MV-Painter&type=Date)](https://www.star-history.com/#amap-cvlab/MV-Painter&Date) -->
