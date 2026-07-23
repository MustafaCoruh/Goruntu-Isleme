"""Shared local-only paths for T.UTYM#2 calibration and model assets."""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALIBRATION_PATH = ROOT / "data" / "tutym2_cam_001.local.json"
DEFAULT_MODEL_PATH = ROOT / "models" / "person_detector.onnx"
TEMPLATE_CALIBRATION_PATH = ROOT / "configs" / "templates" / "tutym2_cam_001.template.json"


def calibration_path() -> Path:
    return Path(os.getenv("FTMC_TUTYM2_CONFIG_PATH", DEFAULT_CALIBRATION_PATH))


def model_path() -> Path:
    return Path(os.getenv("FTMC_PERSON_MODEL_PATH", DEFAULT_MODEL_PATH))
