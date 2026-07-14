"""Run the T.UTYM#2 local photo/video field demo.

Example:
    python scripts/run_tutym2_local_demo.py \
      --config C:\\FTMC_FIELD_DATA\\configs\\tutym2_cam_001.local.json \
      --source C:\\FTMC_FIELD_DATA\\input\\photos\\sample.jpg \
      --model C:\\FTMC_FIELD_DATA\\models\\person_detector.onnx
"""

from __future__ import annotations

from app.field_demo import run


if __name__ == "__main__":
    raise SystemExit(run())
