class FakeFrame:
    shape = (1000, 1000, 3)


class FakeSubtractor:
    def apply(self, frame):
        return "raw-mask"


class FakeCv2:
    THRESH_BINARY = 1
    RETR_EXTERNAL = 2
    CHAIN_APPROX_SIMPLE = 3

    def threshold(self, mask, minimum, maximum, mode):
        return minimum, "binary-mask"

    def findContours(self, mask, retrieval, approximation):
        return ["small", "person"], None

    def contourArea(self, contour):
        return 100 if contour == "small" else 5000

    def boundingRect(self, contour):
        return 10, 20, 30, 40


def test_motion_detector_filters_small_regions_and_returns_boxes():
    from app.vision.motion_detector import OpenCvMotionPersonDetector

    detector = OpenCvMotionPersonDetector(FakeCv2(), FakeSubtractor())
    detections = detector.detect(FakeFrame())

    assert len(detections) == 1
    assert detections[0].class_name == "person"
    assert detections[0].bbox == [10.0, 20.0, 40.0, 60.0]
    assert 0.5 < detections[0].confidence <= 0.75
