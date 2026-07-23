"""Live camera source utilities."""

from app.camera.sources import RtspCameraSource, RtspCameraSourceError

__all__ = [
    "RtspCameraSource",
    "RtspCameraSourceError",
]


def __getattr__(name: str):
    if name in {"ImageFileSource", "ImageFileSourceError"}:
        from app.camera.capture import ImageFileSource, ImageFileSourceError

        return {
            "ImageFileSource": ImageFileSource,
            "ImageFileSourceError": ImageFileSourceError,
        }[name]
    if name in {"RtspCameraSource", "RtspCameraSourceError"}:
        from app.camera.sources import RtspCameraSource, RtspCameraSourceError

        return {
            "RtspCameraSource": RtspCameraSource,
            "RtspCameraSourceError": RtspCameraSourceError,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
