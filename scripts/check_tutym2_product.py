"""Check T.UTYM#2 assets before running a real video."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.product_check import run


if __name__ == "__main__":
    raise SystemExit(run())
