from app.vision.hog_detector import OpenCvHogPersonDetector


class FakeHog:
    def detectMultiScale(self, frame, **kwargs):
        assert kwargs == {"winStride": (8, 8), "padding": (8, 8), "scale": 1.05}
        return [(10, 20, 30, 40)], [2.0]


def test_hog_detector_returns_person_boxes_without_external_model():
    detections = OpenCvHogPersonDetector(FakeHog()).detect(object())

    assert len(detections) == 1
    assert detections[0].class_name == "person"
    assert detections[0].bbox == [10.0, 20.0, 40.0, 60.0]
    assert 0.5 < detections[0].confidence < 1.0
