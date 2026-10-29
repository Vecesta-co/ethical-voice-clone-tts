import numpy as np
from scipy import signal
from typing import Dict
from src.embedding import SpeakerProfile

class AcousticVocoder:
    """Parametric formant vocoder for speech synthesis modulated by speaker acoustic profiles."""

    # Approximate formant frequencies for standard English vowels (F1, F2) in Hz
    VOWEL_FORMANTS: Dict[str, tuple] = {
        "a": (850, 1610),
        "e": (530, 1840),
        "i": (270, 2290),
        "o": (570, 840),
        "u": (300, 870),
    }

    @classmethod
    def synthesize_speech(
        cls,
        text: str,
        profile: SpeakerProfile,
        sample_rate: int = 22050,
        words_per_minute: int = 150
    ) -> np.ndarray:
        """Synthesize continuous audio waveform from text using speaker's acoustic profile."""
        words = text.strip().split()
        if not words:
            return np.zeros(int(sample_rate * 0.5), dtype=np.float32)

        duration_per_word = 60.0 / words_per_minute
        total_samples = []

        f0 = profile.pitch_mean  # Fundamental frequency (Hz)
        f1_base = profile.formant_f1
        f2_base = profile.formant_f2

        for word in words:
            word_clean = word.lower().strip(",.!?")
            vowels = [c for c in word_clean if c in cls.VOWEL_FORMANTS]
            if not vowels:
                vowels = ["e"]

            duration = max(0.2, duration_per_word * (len(word_clean) / 5.0))
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

            # 1. Glottal source excitation (harmonic series with pitch glides)
            f0_contour = f0 * (1.0 + 0.05 * np.sin(2 * np.pi * 3 * t))
            glottal = (
                0.6 * np.sin(2 * np.pi * f0_contour * t)
                + 0.3 * np.sin(2 * np.pi * 2 * f0_contour * t)
                + 0.15 * np.sin(2 * np.pi * 3 * f0_contour * t)
                + 0.08 * np.sin(2 * np.pi * 4 * f0_contour * t)
            )

            # 2. Resonant formant filter
            # Pick dominant vowel formant
            vowel = vowels[0]
            vf1, vf2 = cls.VOWEL_FORMANTS[vowel]
            f1 = (f1_base + vf1) / 2.0
            f2 = (f2_base + vf2) / 2.0

            # Second-order resonant bandpass filters for F1 and F2
            b1, a1 = signal.iirpeak(f1, Q=5.0, fs=sample_rate)
            b2, a2 = signal.iirpeak(f2, Q=6.0, fs=sample_rate)

            filtered1 = signal.lfilter(b1, a1, glottal)
            filtered2 = signal.lfilter(b2, a2, glottal)

            word_audio = 0.6 * filtered1 + 0.4 * filtered2

            # Smooth envelope (attack and decay)
            env = np.ones_like(word_audio)
            ramp_len = min(int(sample_rate * 0.03), len(word_audio) // 4)
            if ramp_len > 0:
                env[:ramp_len] = np.linspace(0, 1, ramp_len)
                env[-ramp_len:] = np.linspace(1, 0, ramp_len)
            word_audio = word_audio * env

            total_samples.append(word_audio)
            # Add short inter-word silence (50 ms)
            total_samples.append(np.zeros(int(sample_rate * 0.05), dtype=np.float32))

        waveform = np.concatenate(total_samples)
        # Normalize peak amplitude
        max_amp = np.max(np.abs(waveform))
        if max_amp > 0:
            waveform = (waveform / max_amp) * 0.85

        return waveform.astype(np.float32)
