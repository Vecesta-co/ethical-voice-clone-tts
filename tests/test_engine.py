import os
import tempfile
import pytest
from src.engine import EthicalVoiceEngine

@pytest.fixture
def test_engine():
    tmp_dir = tempfile.mkdtemp()
    engine = EthicalVoiceEngine(profiles_dir=tmp_dir)
    yield engine
    for f in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, f))
    os.rmdir(tmp_dir)

def test_engine_challenge_and_enroll(test_engine):
    chal = test_engine.request_consent_challenge("Dr. Watson")
    assert "Dr. Watson" in chal["challenge_phrase"]

    with open("fixtures/sample_audio.wav", "rb") as f:
        audio_bytes = f.read()

    profile = test_engine.enroll_voice(
        voice_name="watson",
        audio_bytes=audio_bytes,
        spoken_transcript=chal["challenge_phrase"],
        challenge=chal
    )
    assert profile.voice_name == "watson"
    assert profile.speaker_name == "Dr. Watson"

    # Test load profile
    loaded = test_engine.load_profile("watson")
    assert loaded.voice_name == "watson"

    # Test list voices
    voices = test_engine.list_enrolled_voices()
    assert len(voices) == 1

def test_engine_synthesize_and_verify(test_engine):
    chal = test_engine.request_consent_challenge("Sarah")
    with open("fixtures/sample_audio.wav", "rb") as f:
        audio_bytes = f.read()
    test_engine.enroll_voice("sarah", audio_bytes, chal["challenge_phrase"], chal)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_wav = f.name

    try:
        test_engine.synthesize("sarah", "Testing ethical voice synthesis", out_wav)
        assert os.path.exists(out_wav)
        assert os.path.getsize(out_wav) > 1000

        # Provenance verification check
        prov = test_engine.verify_provenance(out_wav)
        assert prov.is_synthetic is True
        assert prov.speaker_name == "Sarah"
        assert prov.watermark_detected is True
    finally:
        if os.path.exists(out_wav):
            os.remove(out_wav)
