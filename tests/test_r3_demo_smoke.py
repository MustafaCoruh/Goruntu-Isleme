import json

from app.r3_demo_smoke import build_report_payload, run_smoke_checks


def test_run_smoke_checks_passes_for_safe_assets(tmp_path):
    dashboard = tmp_path / "tutym2_dashboard.html"
    dashboard.write_text(
        "T.UTYM#2 Operatör Dashboard\nGüvenli Örnek State Yükle\nR3 Demo Modu\nGerçek görüntü, RTSP URL, IP veya credential göstermez",
        encoding="utf-8",
    )
    example = tmp_path / "state.json"
    example.write_text(
        json.dumps(
            {
                "site": "T.UTYM#2",
                "camera_id": "TUTYM2-CAM-001",
                "tables": [{} for _ in range(14)],
                "safety": {
                    "contains_rtsp_url": False,
                    "contains_credentials": False,
                    "contains_image_or_video": False,
                    "contains_full_local_path": False,
                },
            }
        ),
        encoding="utf-8",
    )

    checks = run_smoke_checks(dashboard=dashboard, example_state=example)
    payload = build_report_payload(checks)

    assert payload["overall_status"] == "pass"
    assert all(check.status == "pass" for check in checks)


def test_run_smoke_checks_fails_for_wrong_table_count(tmp_path):
    dashboard = tmp_path / "tutym2_dashboard.html"
    dashboard.write_text(
        "T.UTYM#2 Operatör Dashboard\nGüvenli Örnek State Yükle\nR3 Demo Modu\nGerçek görüntü, RTSP URL, IP veya credential göstermez",
        encoding="utf-8",
    )
    example = tmp_path / "state.json"
    example.write_text(
        json.dumps(
            {
                "site": "T.UTYM#2",
                "camera_id": "TUTYM2-CAM-001",
                "tables": [{}],
                "safety": {"contains_rtsp_url": False},
            }
        ),
        encoding="utf-8",
    )

    payload = build_report_payload(run_smoke_checks(dashboard=dashboard, example_state=example))

    assert payload["overall_status"] == "fail"


def test_run_smoke_checks_fails_for_unsafe_safety_flag(tmp_path):
    dashboard = tmp_path / "tutym2_dashboard.html"
    dashboard.write_text(
        "T.UTYM#2 Operatör Dashboard\nGüvenli Örnek State Yükle\nR3 Demo Modu\nGerçek görüntü, RTSP URL, IP veya credential göstermez",
        encoding="utf-8",
    )
    example = tmp_path / "state.json"
    example.write_text(
        json.dumps(
            {
                "site": "T.UTYM#2",
                "camera_id": "TUTYM2-CAM-001",
                "tables": [{} for _ in range(14)],
                "safety": {"contains_rtsp_url": True},
            }
        ),
        encoding="utf-8",
    )

    checks = run_smoke_checks(dashboard=dashboard, example_state=example)
    safety = [check for check in checks if check.name == "safety_flags"][0]

    assert safety.status == "fail"
