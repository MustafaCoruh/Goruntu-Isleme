"""Offline Windows readiness checks for T.UTYM#2 field machines.

The checks are intentionally lightweight: they verify Python version, expected
local folders, optional local config/model files, and import availability without
opening cameras or reading real images/videos.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

MIN_PYTHON = (3, 11)
DEFAULT_FIELD_ROOT = r"C:\FTMC_FIELD_DATA"
EXPECTED_SUBDIRS = ("configs", "inputs", "models", "reports")
REQUIRED_IMPORTS = ("json", "argparse", "pathlib")
OPTIONAL_IMPORTS = ("cv2", "numpy", "onnxruntime")


@dataclass(frozen=True)
class CheckResult:
    """Single safe readiness check result."""

    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "message": self.message}


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run safe offline readiness checks for a T.UTYM#2 field machine. "
            "No camera connection is opened and no real media is read."
        )
    )
    parser.add_argument("--field-root", default=DEFAULT_FIELD_ROOT, help="Local field data root folder.")
    parser.add_argument("--config", help="Optional local config JSON path to check for existence.")
    parser.add_argument("--model", help="Optional local ONNX model path to check for existence.")
    parser.add_argument("--report-output", help="Optional safe readiness report JSON path.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    checks = run_readiness_checks(
        field_root=Path(args.field_root).expanduser(),
        config=Path(args.config).expanduser() if args.config else None,
        model=Path(args.model).expanduser() if args.model else None,
    )
    payload = build_report_payload(checks)
    if args.report_output:
        report_output = Path(args.report_output).expanduser()
        if report_output.suffix.lower() != ".json":
            parser.exit(status=2, message="T.UTYM#2 offline readiness failed: report-output must be .json\n")
        report_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["overall_status"] == "pass" else 1


def run_readiness_checks(*, field_root: Path, config: Path | None = None, model: Path | None = None) -> list[CheckResult]:
    """Run safe offline readiness checks without accessing camera/media content."""

    checks: list[CheckResult] = []
    checks.append(_check_python_version())
    checks.extend(_check_imports(REQUIRED_IMPORTS, required=True))
    checks.extend(_check_imports(OPTIONAL_IMPORTS, required=False))
    checks.extend(_check_field_folders(field_root))
    if config is not None:
        checks.append(_check_file(config, "config_file", ".json"))
    if model is not None:
        checks.append(_check_file(model, "model_file", ".onnx"))
    return checks


def build_report_payload(checks: Sequence[CheckResult]) -> dict[str, Any]:
    """Build a safe report payload without full local paths or secrets."""

    has_fail = any(check.status == "fail" for check in checks)
    has_warn = any(check.status == "warn" for check in checks)
    if has_fail:
        overall_status = "fail"
    elif has_warn:
        overall_status = "warn"
    else:
        overall_status = "pass"
    return {
        "report_type": "offline_readiness",
        "site": "T.UTYM#2",
        "overall_status": overall_status,
        "checks": [check.to_dict() for check in checks],
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
        },
    }


def _check_python_version() -> CheckResult:
    current = sys.version_info[:3]
    if current >= MIN_PYTHON:
        return CheckResult("python_version", "pass", f"Python {current[0]}.{current[1]}.{current[2]} is supported.")
    return CheckResult(
        "python_version",
        "fail",
        f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required; current is {current[0]}.{current[1]}.{current[2]}.",
    )


def _check_imports(module_names: Sequence[str], *, required: bool) -> list[CheckResult]:
    results = []
    for module_name in module_names:
        found = importlib.util.find_spec(module_name) is not None
        if found:
            results.append(CheckResult(f"import_{module_name}", "pass", f"{module_name} is available."))
        elif required:
            results.append(CheckResult(f"import_{module_name}", "fail", f"Required module {module_name} is missing."))
        else:
            results.append(CheckResult(f"import_{module_name}", "warn", f"Optional runtime module {module_name} is missing."))
    return results


def _check_field_folders(field_root: Path) -> list[CheckResult]:
    results = []
    for subdir in EXPECTED_SUBDIRS:
        path = field_root / subdir
        if path.is_dir():
            results.append(CheckResult(f"folder_{subdir}", "pass", f"{subdir} folder exists."))
        else:
            results.append(CheckResult(f"folder_{subdir}", "warn", f"{subdir} folder is missing under the field root."))
    return results


def _check_file(path: Path, name: str, expected_suffix: str) -> CheckResult:
    if path.suffix.lower() != expected_suffix:
        return CheckResult(name, "fail", f"Expected a {expected_suffix} file, got {path.name}.")
    if not path.is_file():
        return CheckResult(name, "warn", f"{path.name} was not found locally.")
    return CheckResult(name, "pass", f"{path.name} exists locally.")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
