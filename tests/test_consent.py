import pytest
from src.consent import ConsentManager, ConsentCertificate

def test_generate_challenge():
    chal = ConsentManager.generate_challenge("Alice Smith")
    assert chal["speaker_name"] == "Alice Smith"
    assert len(chal["session_token"]) == 8
    assert "Alice Smith" in chal["challenge_phrase"]
    assert "authorize" in chal["challenge_phrase"]

def test_verify_consent_success():
    audio_dummy = b"RIFF....WAVEfmt...."
    chal = ConsentManager.generate_challenge("Bob Jones")
    spoken = chal["challenge_phrase"]
    cert = ConsentManager.verify_consent(audio_dummy, spoken, chal)

    assert cert.verified is True
    assert cert.speaker_name == "Bob Jones"
    assert cert.session_token == chal["session_token"]
    assert len(cert.audio_sha256) == 64

def test_verify_consent_unauthorized_fails():
    audio_dummy = b"RIFF....WAVEfmt...."
    chal = ConsentManager.generate_challenge("Charlie")
    stolen_speech = "Hey what is going on everyone welcome back to my podcast"

    with pytest.raises(PermissionError):
        ConsentManager.verify_consent(audio_dummy, stolen_speech, chal)
