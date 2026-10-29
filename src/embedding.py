import io
import wave
import numpy as np
from scipy import signal
from typing import List, Optional
from pydantic import BaseModel
from src.consent import ConsentCertificate

class SpeakerProfile(BaseModel):
    """Acoustic speaker embedding and authorized consent record."""
    voice_name: str
    speaker_name: str
    pitch_mean: float  # Fundamental frequency F0 (Hz)
    pitch_std: float
    formant_f1: float  # First formant center (Hz)
    formant_f2: float  # Second formant center (Hz)
    energy_mean: float
    certificate: ConsentCertificate

class SpeakerEmbeddingExtractor:
    """Extracts acoustic prosodic features and formant contours from enrollment WAV audio."""

    @classmethod
    def read_wav(cls, audio_bytes: bytes) -> np.ndarray:
        """Parse raw WAV bytes into a normalized float32 numpy array (-1.0 to 1.0)."""
        with io.BytesIO(audio_bytes) as bio:
            with wave.open(bio, "rb") as wf:
                channels = wf.getnchannels()
                width = wf.getsampwidth()
                frames = wf.readframes(wf.getnframes())

        if width == 2:
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        elif width == 1:
            data = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        else:
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        if channels > 1:
            data = data.reshape(-1, channels).mean(axis=1)

        return data

    @classmethod
    def estimate_pitch_f0(cls, audio: np.ndarray, sample_rate: int = 22050) -> float:
        """Estimate fundamental frequency (F0) using autocorrelation."""
        if len(audio) < 1024:
            return 140.0  # Default neutral pitch

        # Window segment from middle
        mid = len(audio) // 2
        segment = audio[max(0, mid - 2048): min(len(audio), mid + 2048)]
        if len(segment) < 512:
            return 140.0

        # Autocorrelation
        corr = np.correlate(segment, segment, mode="full")
        corr = corr[len(corr)//2:]

        # Pitch range 80 Hz to 350 Hz
        min_lag = int(sample_rate / 350)
        max_lag = int(sample_rate / 80)
        if max_lag >= len(corr):
            max_lag = len(corr) - 1

        if min_lag < max_lag:
            peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
            if peak_lag > 0:
                f0 = float(sample_rate / peak_lag)
                if 70.0 <= f0 <= 400.0:
                    return f0

        return 140.0

    @classmethod
    def extract_profile(
        cls,
        voice_name: str,
        audio_bytes: bytes,
        certificate: ConsentCertificate,
        sample_rate: int = 22050
    ) -> SpeakerProfile:
        """Extract acoustic parameters and bind to consent certificate."""
        audio = cls.read_wav(audio_bytes)
        f0 = cls.estimate_pitch_f0(audio, sample_rate)

        # Estimate simple formant energies via power spectral density
        freqs, psd = signal.welch(audio, fs=sample_rate, nperseg=min(1024, len(audio)))
        # F1 range: 300 to 1000 Hz
        f1_mask = (freqs >= 300) & (freqs <= 1000)
        f1 = float(freqs[f1_mask][np.argmax(psd[f1_mask])]) if any(f1_mask) else 600.0

        # F2 range: 1000 to 2500 Hz
        f2_mask = (freqs >= 1000) & (freqs <= 2500)
        f2 = float(freqs[f2_mask][np.argmax(psd[f2_mask])]) if any(f2_mask) else 1500.0

        energy = float(np.sqrt(np.mean(audio**2)))

        return SpeakerProfile(
            voice_name=voice_name,
            speaker_name=certificate.speaker_name,
            pitch_mean=round(f0, 2),
            pitch_std=round(f0 * 0.1, 2),
            formant_f1=round(f1, 2),
            formant_f2=round(f2, 2),
            energy_mean=round(energy, 4),
            certificate=certificate,
        )
