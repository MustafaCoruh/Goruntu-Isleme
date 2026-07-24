from pathlib import Path

import pytest

from app.model_install import ModelInstallError, install_person_model, validate_person_model


class FakeTensor:
    def __init__(self, name, shape):
        self.name = name
        self.shape = shape


class FakeSession:
    def get_inputs(self):
        return [FakeTensor("images", [1, 3, 416, 416])]

    def get_outputs(self):
        return [FakeTensor("output", [1, 3549, 85])]


def fake_session_factory(*args, **kwargs):
    return FakeSession()


def test_install_person_model_validates_and_copies_atomically(tmp_path):
    source = tmp_path / "yolox_nano.onnx"
    source.write_bytes(b"model" * 300)
    destination = tmp_path / "models" / "person_detector.onnx"

    details = install_person_model(
        source, destination, session_factory=fake_session_factory
    )

    assert destination.read_bytes() == source.read_bytes()
    assert details["input_shape"] == [1, 3, 416, 416]
    assert details["output_shape"] == [1, 3549, 85]
    assert details["installed_to"] == str(destination)


def test_validate_person_model_rejects_small_placeholder(tmp_path):
    source = tmp_path / "person_detector.onnx"
    source.write_text("placeholder", encoding="utf-8")

    with pytest.raises(ModelInstallError, match="kadar küçük"):
        validate_person_model(source, session_factory=fake_session_factory)


def test_validate_person_model_rejects_incompatible_output(tmp_path):
    source = tmp_path / "detector.onnx"
    source.write_bytes(b"model" * 300)

    class IncompatibleSession(FakeSession):
        def get_outputs(self):
            return [FakeTensor("output", [1, 100, 4])]

    with pytest.raises(ModelInstallError, match="Model çıktısı"):
        validate_person_model(
            source, session_factory=lambda *args, **kwargs: IncompatibleSession()
        )
