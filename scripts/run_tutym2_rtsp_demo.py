"""Run the T.UTYM#2 RTSP live-camera test.

Example:
    python scripts/run_tutym2_rtsp_demo.py \
      --config C:\\FTMC_FIELD_DATA\\configs\\tutym2_cam_001.rtsp.local.json \
      --model C:\\FTMC_FIELD_DATA\\models\\person_detector.onnx \
      --report-output C:\\FTMC_FIELD_DATA\\reports\\rtsp_demo_result.json
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.rtsp_field_demo import run


if __name__ == "__main__":
    raise SystemExit(run())
