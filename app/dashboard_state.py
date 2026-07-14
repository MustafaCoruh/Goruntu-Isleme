"""Build a safe T.UTYM#2 dashboard state from local JSON reports."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

DEFAULT_REPORTS_DIR = r"C:\FTMC_FIELD_DATA\reports"
EXPECTED_SITE = "T.UTYM#2"
EXPECTED_CAMERA_ID = "TUTYM2-CAM-001"
EXPECTED_TABLE_COUNT = 14


@dataclass(frozen=True)
class SourceSpec:
    key: str
    filename: str


SOURCE_SPECS = (
    SourceSpec("offline_readiness", "offline_readiness.json"),
    SourceSpec("config_validation", "config_validation_summary.json"),
    SourceSpec("rtsp_connection", "rtsp_connection_test.json"),
    SourceSpec("table_accuracy", "tutym2_table_accuracy_report.json"),
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build safe T.UTYM#2 dashboard state from local report JSON files.")
    parser.add_argument("--reports-dir", default=DEFAULT_REPORTS_DIR, help="Local reports folder.")
    parser.add_argument("--output", help="Optional dashboard_state.json output path.")
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    state = build_dashboard_state(Path(args.reports_dir).expanduser())
    if args.output:
        output = Path(args.output).expanduser()
        if output.suffix.lower() != ".json":
            parser.exit(status=2, message="T.UTYM#2 dashboard state failed: output must be .json\n")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_dashboard_state(reports_dir: Path) -> dict[str, Any]:
    sources = {spec.key: _load_source(reports_dir / spec.filename) for spec in SOURCE_SPECS}
    warnings: list[str] = []
    criticals: list[str] = []

    all_sources_missing = all(source["status"] == "missing" for source in sources.values())
    for key, source in sources.items():
        if source["status"] == "missing":
            if not all_sources_missing:
                warnings.append(f"{key} raporu bulunamadı.")
        elif source["status"] == "invalid_json":
            criticals.append(f"{key} raporu okunamadı; JSON formatı hatalı.")
        elif _safety_violation(source.get("payload")):
            criticals.append(f"{key} raporu güvenli değil; paylaşmayın.")

    _apply_offline_readiness(sources["offline_readiness"].get("payload"), warnings, criticals)
    _apply_config_validation(sources["config_validation"].get("payload"), warnings, criticals)
    connection_status, average_fps = _apply_rtsp_connection(sources["rtsp_connection"].get("payload"), warnings, criticals)
    table_cards, table_summary = _build_table_cards(sources["table_accuracy"].get("payload"), warnings, criticals)

    overall_status = _overall_status(warnings, criticals, sources)
    return {
        "report_type": "dashboard_state",
        "site": EXPECTED_SITE,
        "camera_id": EXPECTED_CAMERA_ID,
        "overall_status": overall_status,
        "connection_status": connection_status,
        "average_fps": average_fps,
        "table_summary": table_summary,
        "tables": table_cards,
        "warnings": warnings,
        "criticals": criticals,
        "sources": {key: {"status": value["status"], "name": value["name"]} for key, value in sources.items()},
        "safety": {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_image_or_video": False,
            "contains_full_local_path": False,
        },
    }


def _load_source(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"name": path.name, "status": "missing", "payload": None}
    try:
        return {"name": path.name, "status": "loaded", "payload": json.loads(path.read_text(encoding="utf-8"))}
    except json.JSONDecodeError:
        return {"name": path.name, "status": "invalid_json", "payload": None}


def _safety_violation(payload: Any) -> bool:
    if not isinstance(payload, Mapping):
        return False
    safety = payload.get("safety")
    if not isinstance(safety, Mapping):
        return False
    return any(value is True for value in safety.values())


def _apply_offline_readiness(payload: Any, warnings: list[str], criticals: list[str]) -> None:
    if not isinstance(payload, Mapping):
        return
    status = payload.get("overall_status")
    if status == "fail":
        criticals.append("Offline readiness fail. Kurulum tamamlanmadan saha demosuna geçmeyin.")
    elif status == "warn":
        warnings.append("Offline readiness warn. Eksik klasör veya opsiyonel modül kontrol edilmeli.")


def _apply_config_validation(payload: Any, warnings: list[str], criticals: list[str]) -> None:
    if not isinstance(payload, Mapping):
        return
    if payload.get("status") != "valid":
        criticals.append("Config doğrulama geçerli değil.")
    if payload.get("table_count") not in (None, EXPECTED_TABLE_COUNT):
        criticals.append("Config içinde 14 masa bekleniyor.")
    resolution = payload.get("resolution")
    if isinstance(resolution, Mapping):
        if resolution.get("width") != 1920 or resolution.get("height") != 1080:
            warnings.append("Config çözünürlüğü beklenen 1920x1080 değil.")


def _apply_rtsp_connection(payload: Any, warnings: list[str], criticals: list[str]) -> tuple[str, float | None]:
    if not isinstance(payload, Mapping):
        return "not_tested", None
    details = payload.get("details") if isinstance(payload.get("details"), Mapping) else {}
    status = payload.get("status")
    requested = details.get("requested_frames")
    read = details.get("frames_read")
    average_fps = details.get("average_fps") if isinstance(details.get("average_fps"), (int, float)) else None
    if status != "connection_test_completed":
        criticals.append("RTSP bağlantı testi tamamlanmadı.")
        return "disconnected", average_fps
    if read == 0:
        criticals.append("RTSP bağlantısında frame okunamadı.")
        return "disconnected", average_fps
    if requested is not None and read != requested:
        warnings.append("RTSP bağlantısı kararsız; okunan frame sayısı beklenenden düşük.")
    if average_fps is not None and average_fps < 5:
        warnings.append("FPS düşük. Ağ, stream profili veya GPU kontrol edilmeli.")
    return "connected", average_fps


def _build_table_cards(payload: Any, warnings: list[str], criticals: list[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    cards = [_empty_table_card(index) for index in range(1, EXPECTED_TABLE_COUNT + 1)]
    summary = {"total": EXPECTED_TABLE_COUNT, "occupied": 0, "empty": 0, "unknown": 0, "no_data": EXPECTED_TABLE_COUNT}
    if not isinstance(payload, Mapping):
        return cards, summary
    report_summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    accuracy = report_summary.get("accuracy")
    if isinstance(accuracy, (int, float)):
        if accuracy < 0.8:
            criticals.append("Model doğruluğu %80 altında. Kalibrasyon/model incelenmeli.")
        elif accuracy < 0.9:
            warnings.append("Model doğruluğu %90 altında; prototip için izlenmeli.")
    if report_summary.get("fn", 0) > 2:
        criticals.append("FN sayısı yüksek; dolu masalar boş sanılıyor olabilir.")

    table_payloads = payload.get("tables") if isinstance(payload.get("tables"), list) else []
    by_id = {item.get("table_id"): item for item in table_payloads if isinstance(item, Mapping)}
    cards = []
    counts = {"occupied": 0, "empty": 0, "unknown": 0, "no_data": 0}
    for index in range(1, EXPECTED_TABLE_COUNT + 1):
        table_id = f"table_{index:02d}"
        item = by_id.get(table_id)
        if item is None:
            card = _empty_table_card(index)
        else:
            state = _normalize_prediction(item.get("prediction"))
            card = {
                "table_id": table_id,
                "display_name": f"Masa {index:02d}",
                "state": state,
                "confidence": item.get("confidence") if isinstance(item.get("confidence"), (int, float)) else None,
                "label": item.get("label") if isinstance(item.get("label"), str) else None,
                "color": _color_for_state(state),
                "warning": _warning_for_label(item.get("label")),
            }
        counts[card["state"]] += 1
        cards.append(card)
    summary = {"total": EXPECTED_TABLE_COUNT, **counts}
    return cards, summary


def _empty_table_card(index: int) -> dict[str, Any]:
    return {
        "table_id": f"table_{index:02d}",
        "display_name": f"Masa {index:02d}",
        "state": "no_data",
        "confidence": None,
        "label": None,
        "color": "gray",
        "warning": "Veri yok.",
    }


def _normalize_prediction(value: Any) -> str:
    if value == "occupied":
        return "occupied"
    if value == "empty":
        return "empty"
    if value == "unknown":
        return "unknown"
    return "no_data"


def _color_for_state(state: str) -> str:
    return {"occupied": "red_or_orange", "empty": "green", "unknown": "yellow", "no_data": "gray"}[state]


def _warning_for_label(label: Any) -> str | None:
    if label == "FP":
        return "Yanlış dolu riski; masa/polygon kontrol edilmeli."
    if label == "FN":
        return "Yanlış boş riski; kritik kontrol gerekli."
    if label == "UNK":
        return "Belirsiz karar; kalibrasyon veya görüş açısı kontrol edilebilir."
    return None


def _overall_status(warnings: Sequence[str], criticals: Sequence[str], sources: Mapping[str, Mapping[str, Any]]) -> str:
    if criticals:
        return "critical"
    if warnings:
        return "warning"
    if all(source["status"] == "missing" for source in sources.values()):
        return "not_ready"
    return "normal"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
