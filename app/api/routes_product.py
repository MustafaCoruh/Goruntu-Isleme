"""Product readiness route for the T.UTYM#2 video workflow."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response

from app.api.routes_occupancy import CURRENT_OCCUPANCY_SNAPSHOT
from app.local_assets import calibration_path, model_path
from app.product_check import check_product_assets
from app.video_test import extract_video_frame, process_video


router = APIRouter(prefix="/product", tags=["product"])
SUPPORTED_VIDEO_EXTENSIONS = {".avi", ".m4v", ".mkv", ".mov", ".mp4"}
MAX_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024


@router.get("/readiness")
def get_product_readiness() -> dict[str, Any]:
    """Return safe readiness checks for the configured calibration and model."""

    config_path, model_path = _asset_paths()
    return check_product_assets(config_path, model_path)


@router.post("/video-test")
async def run_video_test(request: Request) -> dict[str, Any]:
    """Process one uploaded local video without retaining the media file."""

    config_path, model_path = _asset_paths()
    readiness = check_product_assets(config_path, model_path)
    if not readiness["ready_for_video_test"]:
        raise HTTPException(status_code=409, detail=readiness)

    filename = request.headers.get("x-video-filename", "video.mp4")
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Desteklenmeyen video uzantısı.")

    temporary_path: Path | None = None
    received = 0
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
            temporary_path = Path(temporary.name)
            async for chunk in request.stream():
                received += len(chunk)
                if received > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Video 2 GB sınırını aşıyor.")
                temporary.write(chunk)
        if received == 0:
            raise HTTPException(status_code=400, detail="Boş video gönderildi.")

        snapshot = process_video(temporary_path, config_path, model_path)
        CURRENT_OCCUPANCY_SNAPSHOT.clear()
        CURRENT_OCCUPANCY_SNAPSHOT.update(snapshot)
        return {
            "status": "completed",
            "processed_frames": snapshot["processed_frames"],
            "table_count": len(snapshot["tables"]),
        }
    except HTTPException:
        raise
    except Exception as error:
        message = " ".join(str(error).split()) or "Ayrıntı sağlanmadı."
        if temporary_path is not None:
            message = message.replace(str(temporary_path), "<geçici-video>")
        raise HTTPException(
            status_code=422,
            detail=f"Video işlenemedi ({type(error).__name__}): {message[:400]}",
        ) from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


@router.post("/calibration-frame")
async def get_calibration_frame(request: Request) -> Response:
    """Extract one JPEG frame without relying on browser video rendering."""

    filename = request.headers.get("x-video-filename", "video.mp4")
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_VIDEO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Desteklenmeyen video uzantısı.")
    try:
        timestamp = float(request.headers.get("x-video-timestamp", "0"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Geçersiz video zamanı.") from exc
    if timestamp < 0:
        raise HTTPException(status_code=400, detail="Video zamanı negatif olamaz.")

    temporary_path: Path | None = None
    received = 0
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
            temporary_path = Path(temporary.name)
            async for chunk in request.stream():
                received += len(chunk)
                if received > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Video 2 GB sınırını aşıyor.")
                temporary.write(chunk)
        if received == 0:
            raise HTTPException(status_code=400, detail="Boş video gönderildi.")
        try:
            jpeg, width, height = extract_video_frame(temporary_path, timestamp)
        except RuntimeError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return Response(
            content=jpeg,
            media_type="image/jpeg",
            headers={"X-Frame-Width": str(width), "X-Frame-Height": str(height)},
        )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _asset_paths() -> tuple[Path, Path]:
    return calibration_path(), model_path()
