"""Validate safe offline package manifests for T.UTYM#2 handoff.

The manifest is a human-readable JSON checklist for preparing an offline field
package.  It intentionally stores only file names, categories, and yes/no checks;
it must not contain RTSP URLs, credentials, real media names, or full local paths.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

EXPECTED_SITE = "T.UTYM#2"
EXPECTED_PACKAGE_NAME = "tutym2_offline_field_package"
REQUIRED_REPO_ITEMS = {
    "app/field_demo.py",
    "app/rtsp_field_demo.py",
    "app/offline_readiness.py",
    "app/dashboard_state.py",
    "app/dashboard_state_validator.py",
    "configs/templates/tutym2_cam_001.template.json",
    "configs/templates/tutym2_cam_001.rtsp.template.json",
    "configs/templates/tutym2_dashboard_state.example.json",
    "scripts/check_tutym2_offline_readiness.py",
    "scripts/run_tutym2_local_demo.py",
    "scripts/run_tutym2_rtsp_demo.py",
    "scripts/build_tutym2_dashboard_state.py",
    "scripts/validate_tutym2_dashboard_state.py",
    "app/ui/static/tutym2_dashboard.html",
    "docs/deployment/tutym2_field_day_one_page_checklist.md",
}
REQUIRED_LOCAL_ONLY_LABELS = {
    "local_config",
    "local_model",
    "local_input_media",
    "local_reports",
}
FORBIDDEN_KEYWORDS = (
    "rtsp://",
    "password",
    "passwd",
    "credential",
    "secret",
    "token",
)
FULL_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\"),
    re.compile(r"/(?:home|Users|workspace|mnt|media|var|tmp)/"),
)
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


class OfflinePackageManifestError(ValueError):
    """Raised when a package manifest is unsafe or incomplete."""


@dataclass(frozen=True)
class ManifestValidationResult:
    """Safe validation result for an offline package manifest."""

    status: str
    message: str
    repo_item_count: int
    local_only_item_count: int
    handoff_check_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "repo_item_count": self.repo_item_count,
            "local_only_item_count": self.local_only_item_count,
            "handoff_check_count": self.handoff_check_count,
            "safety": {
                "contains_rtsp_url": False,
                "contains_credentials": False,
                "contains_ip_address": False,
                "contains_full_local_path": False,
                "contains_real_media": False,
            },
        }


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a safe T.UTYM#2 offline package manifest JSON without exposing secrets."
    )
    parser.add_argument("manifest", help="Path to the offline package manifest JSON.")
    parser.add_argument("--report-output", help="Optional safe validation result JSON path.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    try:
        result = validate_manifest_file(Path(args.manifest).expanduser())
    except OfflinePackageManifestError as exc:
        parser.exit(status=1, message=f"T.UTYM#2 offline package manifest validation failed: {exc}\n")
    payload = result.to_dict()
    if args.report_output:
        output = Path(args.report_output).expanduser()
        if output.suffix.lower() != ".json":
            parser.exit(status=2, message="T.UTYM#2 offline package manifest validation failed: report-output must be .json\n")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def validate_manifest_file(path: Path) -> ManifestValidationResult:
    if path.suffix.lower() != ".json":
        raise OfflinePackageManifestError("Manifest file must be a .json file.")
    if not path.is_file():
        raise OfflinePackageManifestError("Manifest file was not found.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OfflinePackageManifestError(f"Manifest JSON is invalid: {exc.msg}.") from exc
    return validate_manifest(payload)


def validate_manifest(payload: dict[str, Any]) -> ManifestValidationResult:
    if not isinstance(payload, dict):
        raise OfflinePackageManifestError("Manifest root must be a JSON object.")
    _reject_sensitive_values(payload)
    if payload.get("package_name") != EXPECTED_PACKAGE_NAME:
        raise OfflinePackageManifestError(f"package_name must be {EXPECTED_PACKAGE_NAME}.")
    if payload.get("site") != EXPECTED_SITE:
        raise OfflinePackageManifestError(f"site must be {EXPECTED_SITE}.")

    repo_items = _require_list(payload, "repo_items")
    local_only_items = _require_list(payload, "local_only_items")
    forbidden_items = _require_list(payload, "forbidden_items")
    handoff_checks = _require_list(payload, "handoff_checks")

    repo_paths = {str(item.get("path", "")) for item in repo_items if isinstance(item, dict)}
    missing_repo_items = sorted(REQUIRED_REPO_ITEMS - repo_paths)
    if missing_repo_items:
        raise OfflinePackageManifestError("Missing required repo items: " + ", ".join(missing_repo_items[:5]))

    local_labels = {str(item.get("label", "")) for item in local_only_items if isinstance(item, dict)}
    missing_local_items = sorted(REQUIRED_LOCAL_ONLY_LABELS - local_labels)
    if missing_local_items:
        raise OfflinePackageManifestError("Missing required local-only labels: " + ", ".join(missing_local_items))

    if len(forbidden_items) < 5:
        raise OfflinePackageManifestError("forbidden_items must list at least five forbidden sensitive item categories.")
    if len(handoff_checks) < 6:
        raise OfflinePackageManifestError("handoff_checks must include at least six operator checks.")

    return ManifestValidationResult(
        status="pass",
        message="Offline package manifest is safe and complete for T.UTYM#2 handoff.",
        repo_item_count=len(repo_items),
        local_only_item_count=len(local_only_items),
        handoff_check_count=len(handoff_checks),
    )


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        raise OfflinePackageManifestError(f"{key} must be a non-empty list.")
    return value


def _reject_sensitive_values(value: Any) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _reject_sensitive_values(item)
        return
    if isinstance(value, list):
        for item in value:
            _reject_sensitive_values(item)
        return
    if not isinstance(value, str):
        return
    lowered = value.lower()
    if any(keyword in lowered for keyword in FORBIDDEN_KEYWORDS):
        raise OfflinePackageManifestError("Manifest contains a forbidden sensitive keyword or RTSP-like value.")
    if IP_PATTERN.search(value):
        raise OfflinePackageManifestError("Manifest must not contain IP addresses.")
    if any(pattern.search(value) for pattern in FULL_PATH_PATTERNS):
        raise OfflinePackageManifestError("Manifest must not contain full local paths.")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
