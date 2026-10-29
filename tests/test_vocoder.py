import pytest
import numpy as np
from src.vocoder import AcousticVocoder
from src.embedding import SpeakerProfile
from src.consent import ConsentCertificate

@pytest.fixture
def mock_profile():
    cert = ConsentCertificate(
        speaker_name="Speaker Alpha",
        session_token="ABCDEF12",
        timestamp=1700000000.0,
        challenge_phrase="phrase",
        audio_sha256="hash",
        verified=True
    )
    return SpeakerProfile(
        voice_name="alpha",
        speaker_name="Speaker Alpha",
        pitch_mean=160.0,
        pitch_std=16.0,
        formant_f1=500.0,
        formant_f2=1500.0,
        energy_mean=0.3,
        certificate=cert
    )

def test_synthesize_speech_audio(mock_profile):
    text = "Hello world this is a test"
    waveform = AcousticVocoder.synthesize_speech(text, mock_profile, sample_rate=22050)
    assert isinstance(waveform, np.ndarray)
    assert len(waveform) > 22050 * 0.5  # At least half second
    assert np.max(np.abs(waveform)) <= 1.0

def test_synthesize_empty_text(mock_profile):
    waveform = AcousticVocoder.synthesize_speech("", mock_profile, sample_rate=22050)
    assert len(waveform) > 0
    assert np.all(waveform == 0)
