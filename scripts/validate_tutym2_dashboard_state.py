"""Validate a safe T.UTYM#2 dashboard_state.json file."""

from app.dashboard_state_validator import run

# MERGE-CHECK: keep this operator script for validating dashboard_state.json.


if __name__ == "__main__":
    raise SystemExit(run())
