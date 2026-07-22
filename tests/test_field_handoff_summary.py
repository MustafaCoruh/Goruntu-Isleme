import json

import pytest

from app.field_handoff_summary import (
    FieldHandoffSummaryError,
    ReportInput,
    _parse_input_mapping,
    build_handoff_summary,
)


def _write_report(path, *, status="pass", report_type="offline_readiness", site="T.UTYM#2", safety=None):
    payload = {
        "report_type": report_type,
        "site": site,
        "overall_status": status,
        "safety": safety
        if safety is not None
        else {
            "contains_rtsp_url": False,
            "contains_credentials": False,
            "contains_ip_address": False,
            "contains_full_local_path": False,
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_handoff_summary_passes_for_safe_reports(tmp_path):
    readiness = tmp_path / "offline_readiness.json"
    dashboard = tmp_path / "dashboard_state_validation.json"
    _write_report(readiness, status="pass", report_type="offline_readiness")
    _write_report(dashboard, status="normal", report_type="dashboard_state_validation")

    payload = build_handoff_summary(
        [
            ReportInput("offline_readiness", readiness),
            ReportInput("dashboard_state_validation", dashboard),
        ]
    )

    assert payload["overall_status"] == "normal"
    assert payload["report_count"] == 2
    assert payload["reports"][0]["file_name"] == "offline_readiness.json"
    assert payload["shareable_summary"]["safe_to_share"] is True


def test_build_handoff_summary_promotes_warning(tmp_path):
    report = tmp_path / "offline_readiness.json"
    _write_report(report, status="warn")

    payload = build_handoff_summary([ReportInput("offline_readiness", report)])

    assert payload["overall_status"] == "warning"


def test_build_handoff_summary_promotes_critical(tmp_path):
    report = tmp_path / "offline_readiness.json"
    _write_report(report, status="fail")

    payload = build_handoff_summary([ReportInput("offline_readiness", report)])

    assert payload["overall_status"] == "critical"


def test_build_handoff_summary_rejects_rtsp_text(tmp_path):
    report = tmp_path / "bad.json"
    report.write_text('{"site":"T.UTYM#2","notes":"rtsp://example.invalid/stream"}', encoding="utf-8")

    with pytest.raises(FieldHandoffSummaryError, match="sensitive keyword"):
        build_handoff_summary([ReportInput("rtsp_connection", report)])


def test_build_handoff_summary_rejects_ip_address(tmp_path):
    report = tmp_path / "bad.json"
    report.write_text('{"site":"T.UTYM#2","notes":"192.168.1.50"}', encoding="utf-8")

    with pytest.raises(FieldHandoffSummaryError, match="IP addresses"):
        build_handoff_summary([ReportInput("rtsp_connection", report)])


def test_build_handoff_summary_rejects_wrong_site(tmp_path):
    report = tmp_path / "bad.json"
    _write_report(report, site="OTHER")

    with pytest.raises(FieldHandoffSummaryError, match="site must be"):
        build_handoff_summary([ReportInput("offline_readiness", report)])


def test_parse_input_mapping_rejects_unknown_label():
    with pytest.raises(FieldHandoffSummaryError, match="Unsupported input label"):
        _parse_input_mapping("unknown=report.json")


def test_parse_input_mapping_rejects_non_json():
    with pytest.raises(FieldHandoffSummaryError, match=".json"):
        _parse_input_mapping("offline_readiness=report.txt")
