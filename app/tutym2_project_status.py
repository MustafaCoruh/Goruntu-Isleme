"""Build a safe, shareable T.UTYM#2 project status summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_SITE = "T.UTYM#2"
EXPECTED_CAMERA_ID = "TUTYM2-CAM-001"
SOFTWARE_READINESS_PERCENT = 90


def build_project_status(*, real_r4_files_passed: bool = False) -> dict[str, Any]:
    """Return a non-sensitive project completion summary for operators."""
    remaining = []
    if not real_r4_files_passed:
        remaining.append("Gerçek saha makinesinden gelen 3 güvenli R4 JSON dosyası seçilip PASS vermeli.")

    return {
        "report_type": "tutym2_project_status",
        "site": EXPECTED_SITE,
        "camera_id": EXPECTED_CAMERA_ID,
        "software_ui_docs_percent": SOFTWARE_READINESS_PERCENT,
        "software_ui_docs_status": "largely_ready",
        "field_acceptance_status": "ready_to_close" if real_r4_files_passed else "waiting_for_real_r4_files",
        "can_close_project": real_r4_files_passed,
        "remaining_work": remaining,
        "required_real_r4_files": [
            "Dashboard Durum Raporu",
            "Saha Teslim Özeti",
            "R4 Final Karar Raporu",
        ],
        "safe_to_share": True,
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
            "contains_ip_address": False,
        },
    }


def write_project_status(path: Path, *, real_r4_files_passed: bool = False) -> dict[str, Any]:
    payload = build_project_status(real_r4_files_passed=real_r4_files_passed)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a safe T.UTYM#2 project status JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path.")
    parser.add_argument(
        "--real-r4-files-passed",
        action="store_true",
        help="Mark project closable only after real field R4 JSON files pass.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    write_project_status(args.output, real_r4_files_passed=args.real_r4_files_passed)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
