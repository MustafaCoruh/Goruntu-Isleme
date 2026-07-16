"""Build a safe T.UTYM#2 field handoff summary."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.field_handoff_summary import run


if __name__ == "__main__":
    raise SystemExit(run())
