import json

from app.tutym2_project_status import build_project_status, write_project_status


def test_project_status_waits_for_both_video_validations_by_default():
    payload = build_project_status()

    assert payload["report_type"] == "tutym2_project_status"
    assert payload["site"] == "T.UTYM#2"
    assert payload["camera_id"] == "TUTYM2-CAM-001"
    assert payload["workflow"] == "video_to_table_occupancy"
    assert payload["completion_percent"] == 0
    assert payload["development_video_status"] == "waiting"
    assert payload["camera_video_status"] == "waiting"
    assert payload["can_mark_product_ready"] is False
    assert len(payload["remaining_work"]) == 2
    assert payload["required_manual_json_inputs"] == []
    assert payload["safe_to_share"] is True
    assert all(value is False for value in payload["safety"].values())


def test_project_status_is_half_complete_after_local_video_passes():
    payload = build_project_status(local_video_test_passed=True)

    assert payload["completion_percent"] == 50
    assert payload["development_video_status"] == "passed"
    assert payload["camera_video_status"] == "waiting"
    assert payload["can_mark_product_ready"] is False
    assert len(payload["remaining_work"]) == 1


def test_project_status_is_ready_after_both_video_validations_pass():
    payload = build_project_status(local_video_test_passed=True, camera_video_test_passed=True)

    assert payload["completion_percent"] == 100
    assert payload["can_mark_product_ready"] is True
    assert payload["remaining_work"] == []


def test_write_project_status_writes_safe_json(tmp_path):
    output = tmp_path / "status" / "tutym2_project_status.json"

    payload = write_project_status(output)
    written = json.loads(output.read_text(encoding="utf-8"))

    assert written == payload
    assert written["required_manual_json_inputs"] == []
    assert len(written["required_video_inputs"]) == 2
