"""Run safe T.UTYM#2 offline readiness checks."""

from app.offline_readiness import run


if __name__ == "__main__":
    raise SystemExit(run())
