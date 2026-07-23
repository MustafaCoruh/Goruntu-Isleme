"""Run the T.UTYM#2 local video demo.

Example:
    python scripts/run_tutym2_local_demo.py \
      --config C:\\FTMC_DATA\\configs\\tutym2_cam_001.local.json \
      --source C:\\FTMC_DATA\\videos\\sample.mp4 \
      --model C:\\FTMC_DATA\\models\\person_detector.onnx
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.field_demo import run


if __name__ == "__main__":
    raise SystemExit(run())
