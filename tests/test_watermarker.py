import os
import tempfile
import pytest
import numpy as np
from src.watermarker import AudioWatermarker

def test_watermark_embed_and_detect():
    sr = 44100
    t = np.linspace(0, 1.0, sr, endpoint=False)
    samples = 0.5 * np.sin(2 * np.pi * 300.0 * t).astype(np.float32)

    metadata = {
        "organization": "Vecesta.co",
        "speaker_name": "Verified Alice",
        "session_token": "TOKEN999",
        "timestamp": 1700000000.0,
    }

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name

    try:
        AudioWatermarker.write_watermarked_wav(tmp_path, samples, sr, metadata)
        rec = AudioWatermarker.detect_watermark(tmp_path)

        assert rec.is_synthetic is True
        assert rec.watermark_detected is True
        assert rec.organization == "Vecesta.co"
        assert rec.speaker_name == "Verified Alice"
        assert rec.consent_token == "TOKEN999"
        assert rec.confidence == 1.0
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_detect_watermark_natural_audio():
    # Natural audio fixture should not have synthetic VECS watermark
    rec = AudioWatermarker.detect_watermark("fixtures/sample_audio.wav")
    assert rec.is_synthetic is False
    assert rec.watermark_detected is False
