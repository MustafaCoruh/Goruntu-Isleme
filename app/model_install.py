"""Validate and install a local YOLOX-style ONNX person detector."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

import onnxruntime as ort

from app.local_assets import DEFAULT_MODEL_PATH


class ModelInstallError(ValueError):
    """Raised when a candidate model cannot be safely installed."""


def validate_person_model(
    source: Path,
    *,
    session_factory: Callable[..., Any] = ort.InferenceSession,
) -> dict[str, Any]:
    """Validate that an ONNX file has the detector layout expected by the app."""

    if not source.is_file():
        raise ModelInstallError(f"Model dosyası bulunamadı: {source}")
    if source.suffix.lower() != ".onnx":
        raise ModelInstallError("Model dosyasının uzantısı .onnx olmalıdır.")
    if source.stat().st_size < 1024:
        raise ModelInstallError("Dosya gerçek bir ONNX modeli olamayacak kadar küçük.")

    try:
        session = session_factory(str(source), providers=["CPUExecutionProvider"])
    except Exception as error:
        raise ModelInstallError(
            f"ONNX Runtime modeli açamadı: {type(error).__name__}"
        ) from error

    inputs = session.get_inputs()
    outputs = session.get_outputs()
    if len(inputs) != 1 or len(inputs[0].shape) != 4:
        raise ModelInstallError("Model tek bir 4 boyutlu görüntü girdisi sunmalıdır.")
    if not outputs:
        raise ModelInstallError("Modelin tespit çıktısı bulunamadı.")
    output_shape = outputs[0].shape
    if output_shape and isinstance(output_shape[-1], int) and output_shape[-1] < 6:
        raise ModelInstallError("Model çıktısı kutu, güven ve sınıf değerlerini içermiyor.")

    return {
        "input_name": inputs[0].name,
        "input_shape": list(inputs[0].shape),
        "output_shape": list(output_shape),
        "size_bytes": source.stat().st_size,
    }


def install_person_model(
    source: Path,
    destination: Path = DEFAULT_MODEL_PATH,
    *,
    session_factory: Callable[..., Any] = ort.InferenceSession,
) -> dict[str, Any]:
    """Validate and atomically copy a local model to the product model path."""

    details = validate_person_model(source, session_factory=session_factory)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, suffix=".onnx", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
        try:
            shutil.copy2(source, temporary_path)
            temporary_path.replace(destination)
        finally:
            temporary_path.unlink(missing_ok=True)
    details["installed_to"] = str(destination)
    return details


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Yerel YOLOX-stili ONNX kişi modelini doğrular ve ürüne kurar."
    )
    parser.add_argument("source", type=Path, help="İndirilen .onnx dosyasının yolu")
    parser.add_argument("--destination", type=Path, default=DEFAULT_MODEL_PATH)
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        details = install_person_model(args.source, args.destination)
    except ModelInstallError as error:
        print(f"MODEL KURULAMADI: {error}")
        return 1
    print(f"MODEL KURULDU: {details['installed_to']}")
    print(f"Girdi: {details['input_shape']} | Çıktı: {details['output_shape']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
