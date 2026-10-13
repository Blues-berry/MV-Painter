#!/usr/bin/env python3
"""Build a derived aggregate EGL render view for native_unset scoring.

Sources (read-only):
  - iteration002_bake/native_egl_unseen  : native_unset, no_adapter (220 renders, PASS manifest)
  - bake_matrix_v2/native_egl_unseen     : gt (source-texture alignment condition, already evaluated)

The aggregate view only hardlinks existing renders and merges their manifest rows.
Every row keeps its original render_sha256; the builder re-verifies each file hash.
No existing file is modified. Outputs live under this increment folder.
"""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

EX = Path('/4T/CXY/MV-Painter-1010/1010/experiments/revision_expansion_20261010')
INC = Path('/4T/CXY/MV-Painter/CG_revision_20261011_p0p3_increment/p1_native_unset')
SRC_UNSET = EX / 'iteration002_bake/native_egl_unseen'
SRC_V2 = EX / 'bake_matrix_v2/native_egl_unseen'
AGG = INC / 'outputs/egl_unseen_native_unset_vs_gt'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def link(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def main() -> None:
    assert not AGG.exists(), f'aggregate view already exists: {AGG}'
    m_unset_path = SRC_UNSET / 'GLB_NATIVE_EGL_RENDER_MANIFEST.json'
    m_v2_path = SRC_V2 / 'GLB_NATIVE_EGL_RENDER_MANIFEST.json'
    m_unset = json.loads(m_unset_path.read_text())
    m_v2 = json.loads(m_v2_path.read_text())

    rows_unset = [r for r in m_unset['renders'] if r['method'] in ('native_unset', 'no_adapter')]
    rows_gt = [r for r in m_v2['renders'] if r['method'] == 'gt']
    assert len(rows_unset) == 220 and len(rows_gt) == 110, (len(rows_unset), len(rows_gt))
    assert m_unset['renderer']['sampler_probe']['status'] == 'PASS'
    assert m_v2['renderer']['sampler_probe']['status'] == 'PASS'

    AGG.mkdir(parents=True)
    verified_failures = []
    for row in rows_unset + rows_gt:
        src = (SRC_UNSET if row in rows_unset else SRC_V2) / row['render_path']
        dst = AGG / row['render_path']
        if sha256(src) != row['render_sha256']:
            verified_failures.append(str(src))
            continue
        link(src, dst)
    assert not verified_failures, f'source render hash mismatches: {verified_failures[:5]}'
    # The scorer also reads each <method>/<uid>/bake_metadata.json; link those too.
    metadata_failures = []
    for method, src_root in (('native_unset', SRC_UNSET), ('no_adapter', SRC_UNSET), ('gt', SRC_V2)):
        for uid in sorted({row['render_path'].split('/')[1] for row in (rows_unset if method != 'gt' else rows_gt)}):
            meta_src = src_root / method / uid / 'bake_metadata.json'
            if not meta_src.is_file():
                metadata_failures.append(str(meta_src))
                continue
            link(meta_src, AGG / method / uid / 'bake_metadata.json')
    assert not metadata_failures, f'missing source bake_metadata.json: {metadata_failures[:5]}'

    merged = {
        'status': 'DERIVED_AGGREGATE_RENDER_VIEW_FOR_SCORING',
        'derived_from': [
            {'manifest_path': str(m_unset_path), 'manifest_sha256': sha256(m_unset_path),
             'methods': ['native_unset', 'no_adapter'], 'rows': len(rows_unset)},
            {'manifest_path': str(m_v2_path), 'manifest_sha256': sha256(m_v2_path),
             'methods': ['gt'], 'rows': len(rows_gt)},
        ],
        'note': ('Rows and per-file SHA256 values are copied verbatim from the two source manifests; '
                 'this builder re-verified every file hash before hardlinking. This is not a new '
                 'render run; the gt condition is the source-texture/render alignment sanity '
                 'condition from bake_matrix_v2. No existing experiment file was modified.'),
        'renderer': {**m_unset['renderer'],
                     'provenance': {'native_unset_no_adapter': 'iteration002_bake/native_egl_unseen',
                                    'gt': 'bake_matrix_v2/native_egl_unseen'}},
        'render_count': len(rows_unset) + len(rows_gt),
        'renders': rows_unset + rows_gt,
    }
    merged_path = AGG / 'GLB_NATIVE_EGL_RENDER_MANIFEST.json'
    merged_path.write_text(json.dumps(merged, indent=2, sort_keys=True) + '\n')

    identity = {
        'status': 'COMPLETED',
        'render_count': merged['render_count'],
        'render_manifest_sha256': sha256(merged_path),
        'kind': 'DERIVED_AGGREGATE_FOR_METRIC_SCORING',
        'derived_from': merged['derived_from'],
        'builder_script_sha256': sha256(Path(__file__)),
    }
    (AGG.parent / f'{AGG.name}_RUN_IDENTITY.json').write_text(
        json.dumps(identity, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'BUILT', 'render_count': merged['render_count'],
                      'aggregate_dir': str(AGG)}, indent=2))


if __name__ == '__main__':
    sys.exit(main())
