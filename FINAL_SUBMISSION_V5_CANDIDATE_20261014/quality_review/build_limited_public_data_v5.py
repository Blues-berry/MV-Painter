"""Build a narrow public data deposit from the reviewed V5 evidence archive."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
AUTHOR_NAMES = ["Che, Xueyuan", "Sun, Libo"]
COPYRIGHT_LICENSE = "CC BY 4.0"


def read_csv(zf: zipfile.ZipFile, member: str) -> tuple[list[str], list[dict[str, str]]]:
    with zf.open(member) as stream:
        text = io.TextIOWrapper(stream, encoding="utf-8-sig", newline="")
        reader = csv.DictReader(text)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-zip", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.evidence_zip) as archive:
        rights_fields, rights_rows = read_csv(
            archive, "asset_rights/FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv"
        )
        del rights_fields
        shareable_uids = {
            row["asset_uid"] for row in rights_rows
            if row["final_disposition"] == "METRICS_ONLY"
        }
        if len(shareable_uids) != 271:
            raise ValueError(f"Expected 271 metric-cleared Fresh C assets; found {len(shareable_uids)}")

        datasets = [
            ("data/fresh_c_matched_control_metrics.csv",
             "data/primary_studies/MATCHED300_OBJECT_METRICS.csv", "object_uid", None),
            ("data/fresh_c_equal_budget_contrasts.csv",
             "data/primary_studies/fresh_c_addendum_object_deltas.csv", "object_uid", None),
            ("data/fresh_c_c3_fixed_low_contrasts.csv",
             "data/primary_studies/fresh_c_c3_minus_gfl_object_deltas.csv", "object_uid", None),
            ("data/native_mvadapter_metrics.csv",
             "data/primary_studies/MVADAPTER50_per_object_metrics.csv", "object_uid", None),
            ("data/geotex_bake10_metrics.csv",
             "data/primary_studies/BAKE10_OBJECT_METRICS.csv", "object_uid", None),
        ]
        counts: dict[str, dict[str, int]] = {}
        for destination, member, uid_field, _ in datasets:
            fields, rows = read_csv(archive, member)
            filtered = [row for row in rows if row[uid_field] in shareable_uids]
            write_csv(out / destination, fields, filtered)
            counts[destination] = {
                "records": len(filtered),
                "objects": len({row[uid_field] for row in filtered}),
                "records_in_source": len(rows),
                "objects_in_source": len({row[uid_field] for row in rows}),
            }

        fields, revision_rows = read_csv(
            archive, "data/primary_studies/REVISION_OBJECT_CONDITION_METRICS.csv"
        )
        old5 = [row for row in revision_rows
                if row["source_id"] == "old5_corrected_v3" and row["object_uid"] in shareable_uids]
        write_csv(out / "data/geotex_earlier_bake5_metrics.csv", fields, old5)
        counts["data/geotex_earlier_bake5_metrics.csv"] = {
            "records": len(old5),
            "objects": len({row["object_uid"] for row in old5}),
            "records_in_source": sum(row["source_id"] == "old5_corrected_v3" for row in revision_rows),
            "objects_in_source": len({row["object_uid"] for row in revision_rows
                                      if row["source_id"] == "old5_corrected_v3"}),
        }

        fields, gso_rows = read_csv(archive, "data/GSO100_VIEW_METRICS.csv")
        write_csv(out / "data/gso100_view_metrics.csv", fields, gso_rows)
        counts["data/gso100_view_metrics.csv"] = {
            "records": len(gso_rows),
            "objects": len({row["uid"] for row in gso_rows}),
        }

    expected = {
        "data/fresh_c_matched_control_metrics.csv": (1626, 271),
        "data/fresh_c_equal_budget_contrasts.csv": (813, 271),
        "data/fresh_c_c3_fixed_low_contrasts.csv": (271, 271),
        "data/native_mvadapter_metrics.csv": (301, 43),
        "data/geotex_bake10_metrics.csv": (64, 8),
        "data/geotex_earlier_bake5_metrics.csv": (32, 4),
        "data/gso100_view_metrics.csv": (14400, 100),
    }
    for name, wanted in expected.items():
        got = (counts[name]["records"], counts[name]["objects"])
        if got != wanted:
            raise ValueError(f"Unexpected shareable-row scope for {name}: {got}; expected {wanted}")

    provenance_path = out / "metadata/FIGURE_ASSET_PROVENANCE.csv"
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    source_rows = []
    with (HERE / "figures/FIGURE_ASSET_CREDITS.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            source_rows.append({
                "figure_panel": row["figure_panel"],
                "object_uid": row["object_uid"],
                "source_title": row["title"],
                "creator": row["creator"],
                "source_url": row["source_url"],
                "license": row["license"],
                "license_url": row["license_url"],
                "publication_figure_allowed": row["publication_figure_allowed"],
                "source_file_sha256": row["figure_png_sha256"],
            })
    credited_uids = {row["object_uid"] for row in source_rows}
    with (HERE / "figures/BAKED_ASSET_CREDITS.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["asset_uid"] in credited_uids:
                continue
            section = "S3 and S5" if row["title"] == "LG Remote" else "S5"
            source_rows.append({
                "figure_panel": f"Supplementary Sections {section}",
                "object_uid": row["asset_uid"],
                "source_title": row["title"],
                "creator": row["creator"],
                "source_url": row["original_url"],
                "license": row["license"],
                "license_url": row["license_url"],
                "publication_figure_allowed": row["publication_figure_allowed"],
                "source_file_sha256": "",
            })
    write_csv(provenance_path, list(source_rows[0]), source_rows)

    rights_summary = {
        "rights_source": "FRESH_C_IMAGE_COHORT_ASSET_RIGHTS_20261007.csv",
        "fresh_c_asset_records": 300,
        "metric_only_records_deposited": 271,
        "figure_only_records_not_deposited_as_metrics": 20,
        "rights_unresolved_records_not_deposited": 9,
        "participant_level_data_included": False,
        "source_meshes_or_textures_included": False,
        "generated_image_archives_included": False,
        "model_weights_included": False,
    }
    (out / "metadata/RIGHTS_SCOPE.json").write_text(
        json.dumps(rights_summary, indent=2) + "\n", encoding="utf-8"
    )

    counts_path = out / "metadata/RECORD_COUNTS.json"
    counts_path.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
