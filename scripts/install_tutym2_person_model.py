"""Install a local ONNX person detector from the repository root."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.model_install import run


if __name__ == "__main__":
    raise SystemExit(run())
