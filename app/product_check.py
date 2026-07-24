"""Check whether the local T.UTYM#2 assets are ready for a real video test."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import onnxruntime as ort

from app.tutym2_config_validator import Tutym2ConfigValidationError, validate_config_file
from app.local_assets import DEFAULT_CALIBRATION_PATH, DEFAULT_MODEL_PATH


DEFAULT_CONFIG = DEFAULT_CALIBRATION_PATH
DEFAULT_MODEL = DEFAULT_MODEL_PATH


@dataclass(frozen=True)
class ProductCheck:
    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "message": self.message}


def check_product_assets(
    config_path: Path,
    model_path: Path,
    *,
    session_factory: Callable[..., Any] = ort.InferenceSession,
) -> dict[str, Any]:
    """Validate the calibrated config and ONNX model without opening a video."""

    checks = [
        _check_config(config_path),
        _check_calibration(config_path),
        _check_model(model_path, session_factory=session_factory),
    ]
    ready = all(check.status in {"pass", "warning"} for check in checks)
    return {
        "ready_for_video_test": ready,
        "status": "READY" if ready else "NOT_READY",
        "checks": [check.to_dict() for check in checks],
        "next_step": _next_step(checks),
    }


def _next_step(checks: list[ProductCheck]) -> str:
    failed = {check.name for check in checks if check.status == "fail"}
    if "camera_config" in failed:
        return "Kalibrasyon dosyası geçerli değil. Kalibrasyon ekranında 14 masayı kaydedin."
    if "table_calibration" in failed:
        return "Masa kalibrasyonu tamamlanmadı. Video karesi üzerinde 14 gerçek masa poligonu çizin."
    if "person_model" in failed:
        return "Kalibrasyon hazır ancak kişi dedektörü başlatılamadı. OpenCV kurulumunu kontrol edin."
    if any(check.name == "person_model" and check.status == "warning" for check in checks):
        return "Geliştirme testi hazır: ONNX yerine internet gerektirmeyen OpenCV HOG; HOG yoksa hareket tabanlı dedektör kullanılacak."
    return "Hazır: Lokal T.UTYM#2 videosunu seçip Videoyu İşle düğmesine basın."


def _check_config(path: Path) -> ProductCheck:
    try:
        result = validate_config_file(path)
    except (OSError, json.JSONDecodeError, Tutym2ConfigValidationError) as error:
        return ProductCheck("camera_config", "fail", str(error))
    return ProductCheck("camera_config", "pass", f"{result.table_count} masa yapılandırması geçerli.")


def _check_calibration(path: Path) -> ProductCheck:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return ProductCheck("table_calibration", "fail", str(error))

    tables = payload.get("tables", [])
    has_placeholder = any(
        "PLACEHOLDER" in str(table.get("notes", "")).upper()
        for table in tables
        if isinstance(table, dict)
    )
    if has_placeholder:
        return ProductCheck(
            "table_calibration",
            "fail",
            "Masa poligonları hâlâ şablon değerlerinde; video görüntüsüne göre kalibre edilmelidir.",
        )
    return ProductCheck("table_calibration", "pass", "Masa poligonlarında şablon işareti yok.")


def _check_model(path: Path, *, session_factory: Callable[..., Any]) -> ProductCheck:
    if not path.is_file():
        return ProductCheck(
            "person_model",
            "warning",
            f"{path.name} bulunamadı; OpenCV çevrimdışı geliştirme dedektörü kullanılacak.",
        )
    try:
        session_factory(str(path), providers=["CPUExecutionProvider"])
    except Exception as error:
        return ProductCheck(
            "person_model",
            "warning",
            f"{path.name} geçerli değil ({type(error).__name__}); OpenCV çevrimdışı geliştirme dedektörü kullanılacak.",
        )
    return ProductCheck("person_model", "pass", f"{path.name} ONNX Runtime ile açıldı.")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="T.UTYM#2 video testi öncesi ürün kontrolü.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    result = check_product_assets(args.config, args.model)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready_for_video_test"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
