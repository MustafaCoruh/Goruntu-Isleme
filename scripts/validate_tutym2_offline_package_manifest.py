"""Validate a safe T.UTYM#2 offline package manifest."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.offline_package_manifest import run


if __name__ == "__main__":
    raise SystemExit(run())
