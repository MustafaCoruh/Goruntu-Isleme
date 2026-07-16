"""Run safe T.UTYM#2 R3 dashboard demo smoke checks."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.r3_demo_smoke import run


if __name__ == "__main__":
    raise SystemExit(run())
