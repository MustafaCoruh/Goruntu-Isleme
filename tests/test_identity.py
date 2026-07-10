from app.identity import IdentityMatch, IdentityRecognizer


class StaticIdentityRecognizer:
    def identify(self, frame, detections) -> list[IdentityMatch]:
        return [
            IdentityMatch(
                participant_id="P-001",
                confidence=0.82,
                source="face_recognition",
            )
        ]


def test_identity_match_model_exposes_expected_fields():
    match = IdentityMatch(
        participant_id="P-001",
        confidence=0.82,
        source="face_recognition",
    )

    assert match.participant_id == "P-001"
    assert match.confidence == 0.82
    assert match.source == "face_recognition"


def test_static_recognizer_satisfies_identity_recognizer_protocol():
    recognizer: IdentityRecognizer = StaticIdentityRecognizer()

    matches = recognizer.identify(frame=object(), detections=[])

    assert matches == [
        IdentityMatch(
            participant_id="P-001",
            confidence=0.82,
            source="face_recognition",
        )
    ]
