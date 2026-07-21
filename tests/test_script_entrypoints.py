import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "script_name",
    [
        "check_tutym2_product.py",
        "run_tutym2_local_demo.py",
        "run_tutym2_rtsp_demo.py",
        "validate_tutym2_config.py",
        "validate_tutym2_table_accuracy_report.py",
    ],
)
def test_script_can_be_started_directly_from_repository(script_name):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script_name), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout.lower()
