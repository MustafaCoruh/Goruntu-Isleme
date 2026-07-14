from app.offline_readiness import CheckResult, build_report_payload, run_readiness_checks


def test_build_report_payload_pass():
    payload = build_report_payload([CheckResult("x", "pass", "ok")])

    assert payload["overall_status"] == "pass"
    assert payload["safety"]["contains_rtsp_url"] is False


def test_build_report_payload_warn_precedes_pass():
    payload = build_report_payload([CheckResult("x", "pass", "ok"), CheckResult("y", "warn", "missing")])

    assert payload["overall_status"] == "warn"


def test_build_report_payload_fail_precedes_warn():
    payload = build_report_payload([CheckResult("x", "warn", "missing"), CheckResult("y", "fail", "bad")])

    assert payload["overall_status"] == "fail"


def test_run_readiness_checks_reports_expected_folders(tmp_path):
    for subdir in ("configs", "inputs", "models", "reports"):
        (tmp_path / subdir).mkdir()

    checks = run_readiness_checks(field_root=tmp_path)
    folder_checks = {check.name: check.status for check in checks if check.name.startswith("folder_")}

    assert folder_checks == {
        "folder_configs": "pass",
        "folder_inputs": "pass",
        "folder_models": "pass",
        "folder_reports": "pass",
    }


def test_run_readiness_checks_checks_optional_config_and_model(tmp_path):
    config = tmp_path / "local.json"
    model = tmp_path / "person_detector.onnx"
    config.write_text("{}", encoding="utf-8")
    model.write_text("model", encoding="utf-8")

    checks = run_readiness_checks(field_root=tmp_path, config=config, model=model)
    statuses = {check.name: check.status for check in checks}

    assert statuses["config_file"] == "pass"
    assert statuses["model_file"] == "pass"


def test_run_readiness_checks_rejects_wrong_suffix(tmp_path):
    checks = run_readiness_checks(field_root=tmp_path, config=tmp_path / "config.txt", model=tmp_path / "model.bin")
    statuses = {check.name: check.status for check in checks}

    assert statuses["config_file"] == "fail"
    assert statuses["model_file"] == "fail"
