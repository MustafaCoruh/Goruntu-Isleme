"""R3 dashboard demo smoke checks for T.UTYM#2.

These checks validate that the static dashboard demo assets are present and that
safe example JSON can support a no-real-data dashboard presentation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

EXPECTED_SITE = "T.UTYM#2"
EXPECTED_CAMERA_ID = "TUTYM2-CAM-001"
EXPECTED_TABLE_COUNT = 14
DEFAULT_DASHBOARD = Path("app/ui/static/tutym2_dashboard.html")
DEFAULT_EXAMPLE_STATE = Path("configs/templates/tutym2_dashboard_state.example.json")
REQUIRED_DASHBOARD_TEXT = (
    "T.UTYM#2 Operatör Dashboard",
    "Güvenli Örnek State Yükle",
    "Gerçek görüntü, RTSP URL, IP veya credential göstermez",
)


class R3DemoSmokeError(ValueError):
    """Raised when R3 dashboard demo smoke checks fail."""


@dataclass(frozen=True)
class SmokeCheck:
    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "message": self.message}


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run safe T.UTYM#2 R3 dashboard demo smoke checks.")
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD), help="Static dashboard HTML path.")
    parser.add_argument("--example-state", default=str(DEFAULT_EXAMPLE_STATE), help="Safe dashboard state example JSON path.")
    parser.add_argument("--report-output", help="Optional safe smoke report JSON path.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    checks = run_smoke_checks(dashboard=Path(args.dashboard), example_state=Path(args.example_state))
    payload = build_report_payload(checks)
    if args.report_output:
        output = Path(args.report_output).expanduser()
        if output.suffix.lower() != ".json":
            parser.exit(status=2, message="T.UTYM#2 R3 demo smoke failed: report-output must be .json\n")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["overall_status"] == "pass" else 1


def run_smoke_checks(*, dashboard: Path, example_state: Path) -> list[SmokeCheck]:
    checks: list[SmokeCheck] = []
    checks.extend(_check_dashboard(dashboard))
    checks.extend(_check_example_state(example_state))
    return checks


def build_report_payload(checks: Sequence[SmokeCheck]) -> dict[str, Any]:
    overall_status = "fail" if any(check.status == "fail" for check in checks) else "pass"
    return {
        "report_type": "r3_dashboard_demo_smoke",
        "site": EXPECTED_SITE,
        "overall_status": overall_status,
        "checks": [check.to_dict() for check in checks],
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
        },
    }


def _check_dashboard(path: Path) -> list[SmokeCheck]:
    if not path.is_file():
        return [SmokeCheck("dashboard_file", "fail", f"{path.name} was not found.")]
    text = path.read_text(encoding="utf-8")
    checks = [SmokeCheck("dashboard_file", "pass", f"{path.name} exists.")]
    for required in REQUIRED_DASHBOARD_TEXT:
        status = "pass" if required in text else "fail"
        checks.append(SmokeCheck(f"dashboard_text_{_slug(required)}", status, f"Required dashboard text checked: {required}"))
    return checks


def _check_example_state(path: Path) -> list[SmokeCheck]:
    if not path.is_file():
        return [SmokeCheck("example_state_file", "fail", f"{path.name} was not found.")]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [SmokeCheck("example_state_json", "fail", f"Example state JSON is invalid: {exc.msg}.")]

    checks = [SmokeCheck("example_state_file", "pass", f"{path.name} exists.")]
    checks.append(_value_check("site", payload.get("site"), EXPECTED_SITE))
    checks.append(_value_check("camera_id", payload.get("camera_id"), EXPECTED_CAMERA_ID))
    tables = payload.get("tables")
    table_count = len(tables) if isinstance(tables, list) else 0
    checks.append(_value_check("table_count", table_count, EXPECTED_TABLE_COUNT))
    checks.append(_safety_check(payload.get("safety")))
    return checks


def _value_check(name: str, actual: Any, expected: Any) -> SmokeCheck:
    status = "pass" if actual == expected else "fail"
    return SmokeCheck(name, status, f"Expected {expected}; got {actual}.")


def _safety_check(safety: Any) -> SmokeCheck:
    if not isinstance(safety, dict):
        return SmokeCheck("safety_flags", "fail", "Safety object is missing.")
    unsafe = [key for key, value in safety.items() if value is True]
    if unsafe:
        return SmokeCheck("safety_flags", "fail", "Unsafe true safety flags: " + ", ".join(sorted(unsafe)))
    return SmokeCheck("safety_flags", "pass", "All example safety flags are false.")


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")[:48]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
