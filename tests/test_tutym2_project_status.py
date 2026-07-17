import json

from app.tutym2_project_status import build_project_status, write_project_status


def test_project_status_waits_for_real_r4_files_by_default():
    payload = build_project_status()

    assert payload["report_type"] == "tutym2_project_status"
    assert payload["site"] == "T.UTYM#2"
    assert payload["camera_id"] == "TUTYM2-CAM-001"
    assert payload["software_ui_docs_percent"] == 90
    assert payload["field_acceptance_status"] == "waiting_for_real_r4_files"
    assert payload["can_close_project"] is False
    assert payload["remaining_work"]
    assert payload["safe_to_share"] is True
    assert all(value is False for value in payload["safety"].values())


def test_project_status_can_close_only_after_real_r4_files_pass():
    payload = build_project_status(real_r4_files_passed=True)

    assert payload["field_acceptance_status"] == "ready_to_close"
    assert payload["can_close_project"] is True
    assert payload["remaining_work"] == []


def test_write_project_status_writes_safe_json(tmp_path):
    output = tmp_path / "status" / "tutym2_project_status.json"

    payload = write_project_status(output)
    written = json.loads(output.read_text(encoding="utf-8"))

    assert written == payload
    assert "Dashboard Durum Raporu" in written["required_real_r4_files"]
