import pytest

from app.offline_package_manifest import OfflinePackageManifestError, validate_manifest


def _valid_manifest():
    return {
        "package_name": "tutym2_offline_field_package",
        "site": "T.UTYM#2",
        "repo_items": [
            {"path": "app/field_demo.py"},
            {"path": "app/rtsp_field_demo.py"},
            {"path": "app/offline_readiness.py"},
            {"path": "app/dashboard_state.py"},
            {"path": "app/dashboard_state_validator.py"},
            {"path": "configs/templates/tutym2_cam_001.template.json"},
            {"path": "configs/templates/tutym2_cam_001.rtsp.template.json"},
            {"path": "configs/templates/tutym2_dashboard_state.example.json"},
            {"path": "scripts/check_tutym2_offline_readiness.py"},
            {"path": "scripts/run_tutym2_local_demo.py"},
            {"path": "scripts/run_tutym2_rtsp_demo.py"},
            {"path": "scripts/build_tutym2_dashboard_state.py"},
            {"path": "scripts/validate_tutym2_dashboard_state.py"},
            {"path": "app/ui/static/tutym2_dashboard.html"},
            {"path": "docs/deployment/tutym2_field_day_one_page_checklist.md"},
        ],
        "local_only_items": [
            {"label": "local_config"},
            {"label": "local_model"},
            {"label": "local_input_media"},
            {"label": "local_reports"},
        ],
        "forbidden_items": [
            "real stream value",
            "camera network value",
            "camera username",
            "camera passphrase",
            "real room photo",
        ],
        "handoff_checks": [
            "repo synced",
            "field folder exists",
            "local config stays local",
            "model stays local",
            "readiness report produced",
            "dashboard state validated",
        ],
    }


def test_validate_manifest_passes_for_safe_manifest():
    result = validate_manifest(_valid_manifest())

    assert result.status == "pass"
    assert result.repo_item_count == 15
    assert result.to_dict()["safety"]["contains_rtsp_url"] is False


def test_validate_manifest_rejects_wrong_site():
    manifest = _valid_manifest()
    manifest["site"] = "OTHER"

    with pytest.raises(OfflinePackageManifestError, match="site must be"):
        validate_manifest(manifest)


def test_validate_manifest_rejects_missing_required_repo_item():
    manifest = _valid_manifest()
    manifest["repo_items"] = manifest["repo_items"][:-1]

    with pytest.raises(OfflinePackageManifestError, match="Missing required repo items"):
        validate_manifest(manifest)


def test_validate_manifest_rejects_missing_local_only_label():
    manifest = _valid_manifest()
    manifest["local_only_items"] = [{"label": "local_config"}]

    with pytest.raises(OfflinePackageManifestError, match="Missing required local-only labels"):
        validate_manifest(manifest)


def test_validate_manifest_rejects_sensitive_values():
    manifest = _valid_manifest()
    manifest["notes"] = "rtsp://example.invalid/stream"

    with pytest.raises(OfflinePackageManifestError, match="sensitive keyword"):
        validate_manifest(manifest)


def test_validate_manifest_rejects_ip_addresses():
    manifest = _valid_manifest()
    manifest["notes"] = "camera address 192.168.1.10"

    with pytest.raises(OfflinePackageManifestError, match="IP addresses"):
        validate_manifest(manifest)
