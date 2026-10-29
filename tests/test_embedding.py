import pytest
import numpy as np
from src.embedding import SpeakerEmbeddingExtractor
from src.consent import ConsentCertificate

@pytest.fixture
def sample_wav_bytes():
    with open("fixtures/sample_audio.wav", "rb") as f:
        return f.read()

@pytest.fixture
def dummy_certificate():
    return ConsentCertificate(
        speaker_name="Test Speaker",
        session_token="TEST1234",
        timestamp=1700000000.0,
        challenge_phrase="test phrase",
        audio_sha256="abc123hash",
        verified=True
    )

def test_read_wav(sample_wav_bytes):
    samples = SpeakerEmbeddingExtractor.read_wav(sample_wav_bytes)
    assert isinstance(samples, np.ndarray)
    assert len(samples) > 1000
    assert np.max(np.abs(samples)) <= 1.0

def test_estimate_pitch_f0(sample_wav_bytes):
    samples = SpeakerEmbeddingExtractor.read_wav(sample_wav_bytes)
    f0 = SpeakerEmbeddingExtractor.estimate_pitch_f0(samples, 22050)
    # The fixture was synthesized with 180 Hz sine wave
    assert 160.0 <= f0 <= 200.0

def test_extract_profile(sample_wav_bytes, dummy_certificate):
    profile = SpeakerEmbeddingExtractor.extract_profile(
        voice_name="test_voice",
        audio_bytes=sample_wav_bytes,
        certificate=dummy_certificate,
        sample_rate=22050
    )
    assert profile.voice_name == "test_voice"
    assert profile.speaker_name == "Test Speaker"
    assert profile.pitch_mean > 0
    assert profile.formant_f1 > 0
    assert profile.formant_f2 > profile.formant_f1
