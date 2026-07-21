"""Validate a local T.UTYM#2 table accuracy report."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.table_accuracy_report import run


if __name__ == "__main__":
    raise SystemExit(run())
