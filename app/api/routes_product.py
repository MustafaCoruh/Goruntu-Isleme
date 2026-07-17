"""Product readiness route for the T.UTYM#2 video workflow."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from app.product_check import check_product_assets


router = APIRouter(prefix="/product", tags=["product"])
ROOT = Path(__file__).resolve().parents[2]


@router.get("/readiness")
def get_product_readiness() -> dict[str, Any]:
    """Return safe readiness checks for the configured calibration and model."""

    config_path = Path(
        os.getenv(
            "FTMC_TUTYM2_CONFIG_PATH",
            ROOT / "configs" / "templates" / "tutym2_cam_001.template.json",
        )
    )
    model_path = Path(
        os.getenv(
            "FTMC_PERSON_MODEL_PATH",
            ROOT / "models" / "person_detector.onnx",
        )
    )
    return check_product_assets(config_path, model_path)
