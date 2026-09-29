# Round 2 GLB 原始资产恢复审计

更新日期：2026-09-28

## 结论

本轮缺失的 10 个 GLB 已全部恢复为 Exact Mesh。10/10 均命中 Objaverse-XL Smithsonian 官方 annotations；官方 downloader 返回 10 个 `FOUND`、0 个 `MODIFIED`、0 个 `MISSING`，下载文件的实际 SHA-256 与官方 metadata 中的 SHA-256 全部一致。

因此，当前 100-object MV-Adapter cohort 的几何输入已经满足 Exact-only 启动条件。此前的 mixed-proxy 结果仍是历史诊断结果，没有被覆盖，也没有升级为 Exact 结果。

完整逐对象记录见 [GLB_RECOVERY_MANIFEST.json](./GLB_RECOVERY_MANIFEST.json)。

## UID v5 反查

UUID v5 不能从 UUID 字符串直接反解 URL。本次使用已安装的 `objaverse==0.1.7` 官方实现，对官方 Smithsonian annotations 的 `fileIdentifier` 重新计算：

```python
uuid.uuid5(uuid.NAMESPACE_DNS, fileIdentifier)
```

annotations 通过 `objaverse.xl.smithsonian.SmithsonianDownloader.get_annotations(download_dir="/home/ubuntu/.objaverse", refresh=False)` 获取，共 2,407 行；10 个 UID 全部精确匹配 Smithsonian 行。官方 Objaverse v1 的 62,414-object list 未命中这 10 个 UID，因此没有把它们错误地交给 Objaverse 1.0 `load_objects()`。

annotations 缓存：`/home/ubuntu/.objaverse/smithsonian/smithsonian.parquet`

annotations SHA-256：`e8dc6d4eb8035f174dc518449f6eea3e5d5d55084b9891371db8ae0141259ae5`

## 逐对象结果

| object | UID | Smithsonian metadata title | SHA-256 | 分类 |
|---|---|---|---|---|
| obj_0013 | `ed8653d0-c70c-53dc-80e6-53228d51fa1b` | Macaca nemestrina: Cranium | `9b528937ab4b170869dfbabdf7977cf590ba2b60415c72a74e00075ed6dd34db` | Exact |
| obj_0015 | `eda4277e-9984-5ff7-9891-ad816c3f09fc` | Pan troglodytes troglodytes: Cuneiform3 Left | `076f7af92c54f1f32bbf4bd0c093f681091c018b063e4e457301bdaf945500b7` | Exact |
| obj_0038 | `f1d9357b-e4dc-5795-8f21-83f1fd367732` | Gorilla beringei beringei: Cuboid Left | `55cae3e3c1b3829e62fbb90016dc9b743cb87ed326c6a09ed53967d9d124b205` | Exact |
| obj_0048 | `f41b5880-69c0-5c0e-846f-f631250acde3` | Carnegie Mansion: Interior | `eae94e9008d794e2fe5ff2292056cb2101e9abf36d20f7ab4cf72884d5119ff1` | Exact |
| obj_0054 | `f49b18b0-4668-569f-84a7-4338339bf65d` | Cebus versicolor: Mandible | `9f708337a1b43551750d02c73f0a840955f6f697c1d5d7bdb696a363f7b7c3a8` | Exact |
| obj_0066 | `f74207ca-8dd4-50f8-b0fd-eea2eac89270` | Pongo abelii: Talus Left | `39b444e0f9d5342a852c1e3a8f31a31ff97c0a0c3f29ebda715623d13b8ff370` | Exact |
| obj_0068 | `f79d049c-b5aa-554e-aeff-c315e64d034b` | Pongo pygmaeus: cranium | `de9a926f8cca61b63dfdc39ac35d94b5f4d6d9b61de232dc9e215a6a79c62106` | Exact |
| obj_0078 | `f979eb16-0223-54c9-bb01-a2fb908a0ea5` | Pan troglodytes: Ulna Left | `a3262d93cbcff80289e68315187914e5f01ef533b7b7e686a38f14da93107f1b` | Exact |
| obj_0082 | `fa0ecf81-8069-59fc-bda2-7a734833388b` | Pongo abelii: MT5 Right | `3997f3b67117e1d1cfa8cac00e99901ad16e6acb44ae4b7b54f07edbc8eb98a1` | Exact |
| obj_0083 | `fa19ccee-da9b-5b19-9b9d-f67548eb10ed` | apron | `1bed1422879d1678de2e8a3af57740b30d0c2d2365bfd103b8d23671c42fcb8a` | Exact |

原始下载 URL、`fileIdentifier`、expected SHA、actual SHA、文件大小、几何统计和逐对象验证数据均保存在 JSON manifest 中。下载来源全部为 Smithsonian `https://3d-api.si.edu/.../*.glb`。

## 严格验证

- 每个 GLB 均以 `trimesh.load(..., force="scene", process=False)` 成功加载，并包含有效非空几何体。
- 使用历史 renderer `archive3.0/archive2.0/root_legacy/data_process/blender_script.py` 重放 17 个原始相机视角。
- 10 个对象的所有渲染 mask 非空；跨对象/视角的最低 mask IoU 为 `0.9994854202`。
- 每对象平均 depth absolute error 最大为 `7.5232547e-06`，normal absolute error 最大为 `1.6783636e-05`。
- GT 对齐输出保存在 `recovered_legacy_validation_all/`，不是由 GT 深度反构的 mesh。

原归档 HDRI 路径已不存在，因此严格重放使用服务器上已有的 `studio_small_03_1k.hdr`。这会限制光照 provenance 的声明，但不改变本次 mesh、camera、normalization、mask、depth 的来源判定；该限制已写入 manifest。`repair_empty_render.py` 的 bbox 处理也已改为 evaluated mesh vertices，以匹配历史 renderer 的几何范围计算。

## 分类统计

| Exact | Modified | Proxy | Missing |
|---:|---:|---:|---:|
| 10 | 0 | 0 | 0 |

本次恢复没有使用类别相似替代物，也没有把 proxy mesh 称为原始资产。`proxy_meshes/`（若存在）仅保留为此前诊断记录。

## 已执行命令摘要

```bash
python -c 'from objaverse.xl.smithsonian import SmithsonianDownloader; ... get_annotations(...)'
python -c 'from objaverse.utils import get_uid_from_str; ... derive UID from fileIdentifier and filter missing UIDs'
python -c 'from objaverse.xl import download_objects; ... download matched Smithsonian rows with processes=1'
sha256sum final/round2/mv_adapter/recovered_exact_meshes/*.glb
python -c 'import trimesh; trimesh.load(path, force="scene", process=False)'
blender-4.2.4 --background --python archive3.0/archive2.0/root_legacy/data_process/blender_script.py -- \
  --object_path <uid>.glb --output_dir final/round2/mv_adapter/recovered_legacy_validation_all \
  --object_uid <object_id> --hdri_path <studio_small_03_1k.hdr>
```

实际命令和结果摘要以 JSON manifest 为准。

## Exact Protocol 状态

恢复本身已经满足正式 Exact-only 实验的输入启动条件：10 个缺失对象都有可追溯的官方来源和匹配 SHA。此前 mixed-proxy calibration/holdout 输出必须继续作为历史诊断保存；不能与新的 Exact 输出混成一个 cohort。

冻结的 calibration rule 没有修改。Exact calibration 已完成 24 objects × 12 schedules = 288 行，得到 Pareto pair：`fixed_low`（0.75，conservative）与 `fixed_1.0`（aggressive），状态为 `clear_tradeoff`；stage 八组合已全部报告，但冻结 rule 没有定义唯一 winner。

Exact holdout 已完成 76 objects × 5 个有定义 schedule = 380 行：`no_geometry`、`fixed_low`、`fixed_1.0`、`linear_warmup`、`cosine_bump`。所有行均为 `exact_mesh`，所有指标 finite；10,000-resample paired bootstrap 保存在 `results/holdout_exact_76/paired_bootstrap_exact.json`。由于 stage rule 没有唯一 winner，`cai_calibrated_schedule` 没有合法定义，因此没有事后挑选一个 schedule，也不声称已完成预注册的完整六比较。

Exact calibration/holdout 的完整路径、CSV SHA、analysis SHA 和 bootstrap SHA 均已写入 `GLB_RECOVERY_MANIFEST.json`。

Codex A 的受控主适配器 checkpoint 已存在并应继续使用；本审计不把它标记为缺失。它是受控重训 artifact，不等同于恢复历史 v1 checkpoint，具体 SHA 和路径以 Codex A 审计为准。
