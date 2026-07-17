"""Build a T.UTYM#2 video-validation project status summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_SITE = "T.UTYM#2"
EXPECTED_CAMERA_ID = "TUTYM2-CAM-001"


def build_project_status(
    *,
    local_video_test_passed: bool = False,
    camera_video_test_passed: bool = False,
) -> dict[str, Any]:
    """Return progress based on the two real video-validation milestones."""
    remaining = []
    if not local_video_test_passed:
        remaining.append("T.UTYM#2'den alınmış lokal geçmiş video ile 14 masa doluluk testi yapılmalı.")
    if not camera_video_test_passed:
        remaining.append("Canlı kamera akışı veya eski kamera kaydı ile ürün doğrulaması yapılmalı.")

    completed_milestones = int(local_video_test_passed) + int(camera_video_test_passed)

    return {
        "report_type": "tutym2_project_status",
        "site": EXPECTED_SITE,
        "camera_id": EXPECTED_CAMERA_ID,
        "workflow": "video_to_table_occupancy",
        "target": "14 masanın dolu veya boş olduğunu belirlemek",
        "completion_percent": completed_milestones * 50,
        "development_video_status": "passed" if local_video_test_passed else "waiting",
        "camera_video_status": "passed" if camera_video_test_passed else "waiting",
        "can_mark_product_ready": local_video_test_passed and camera_video_test_passed,
        "remaining_work": remaining,
        "required_video_inputs": [
            "Geliştirme için T.UTYM#2 lokal geçmiş videosu",
            "Ürün doğrulaması için canlı kamera akışı veya eski kamera kaydı",
        ],
        "required_manual_json_inputs": [],
        "safe_to_share": True,
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
            "contains_ip_address": False,
        },
    }


def write_project_status(
    path: Path,
    *,
    local_video_test_passed: bool = False,
    camera_video_test_passed: bool = False,
) -> dict[str, Any]:
    payload = build_project_status(
        local_video_test_passed=local_video_test_passed,
        camera_video_test_passed=camera_video_test_passed,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a safe T.UTYM#2 project status JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path.")
    parser.add_argument(
        "--local-video-test-passed",
        action="store_true",
        help="Mark the local historical-video occupancy test as passed.",
    )
    parser.add_argument(
        "--camera-video-test-passed",
        action="store_true",
        help="Mark live-camera or recorded-camera video validation as passed.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    write_project_status(
        args.output,
        local_video_test_passed=args.local_video_test_passed,
        camera_video_test_passed=args.camera_video_test_passed,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
