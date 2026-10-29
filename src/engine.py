import os
import json
import time
from typing import Dict, List, Optional
from src.consent import ConsentManager, ConsentCertificate
from src.embedding import SpeakerProfile, SpeakerEmbeddingExtractor
from src.vocoder import AcousticVocoder
from src.watermarker import AudioWatermarker, ProvenanceRecord

class EthicalVoiceEngine:
    """End-to-end consent-verified voice cloning and synthesis engine."""

    def __init__(self, profiles_dir: str = "voices", sample_rate: int = 22050):
        self.profiles_dir = profiles_dir
        self.sample_rate = sample_rate
        os.makedirs(self.profiles_dir, exist_ok=True)

    def request_consent_challenge(self, speaker_name: str) -> Dict[str, str]:
        """Step 1: Generate dynamic challenge phrase for the speaker to read."""
        return ConsentManager.generate_challenge(speaker_name)

    def enroll_voice(
        self,
        voice_name: str,
        audio_bytes: bytes,
        spoken_transcript: str,
        challenge: Dict[str, str]
    ) -> SpeakerProfile:
        """Step 2: Validate vocal consent and extract acoustic speaker embedding."""
        cert = ConsentManager.verify_consent(audio_bytes, spoken_transcript, challenge)
        profile = SpeakerEmbeddingExtractor.extract_profile(
            voice_name=voice_name,
            audio_bytes=audio_bytes,
            certificate=cert,
            sample_rate=self.sample_rate,
        )

        profile_path = os.path.join(self.profiles_dir, f"{voice_name}.json")
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))

        return profile

    def load_profile(self, voice_name: str) -> SpeakerProfile:
        """Load an enrolled speaker profile from disk."""
        profile_path = os.path.join(self.profiles_dir, f"{voice_name}.json")
        if not os.path.exists(profile_path):
            raise FileNotFoundError(f"Enrolled voice '{voice_name}' not found in {self.profiles_dir}.")

        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SpeakerProfile(**data)

    def synthesize(
        self,
        voice_name: str,
        text: str,
        output_wav_path: str,
        words_per_minute: int = 150
    ) -> str:
        """Step 3: Synthesize speech and automatically inject inaudible provenance watermark."""
        profile = self.load_profile(voice_name)
        raw_waveform = AcousticVocoder.synthesize_speech(
            text=text,
            profile=profile,
            sample_rate=self.sample_rate,
            words_per_minute=words_per_minute,
        )

        now = time.time()
        metadata = {
            "is_synthetic": True,
            "organization": "Vecesta.co",
            "voice_name": voice_name,
            "speaker_name": profile.speaker_name,
            "session_token": profile.certificate.session_token,
            "timestamp": now,
            "certificate_id": profile.certificate.certificate_id,
        }

        AudioWatermarker.write_watermarked_wav(
            output_path=output_wav_path,
            audio_samples=raw_waveform,
            sample_rate=self.sample_rate,
            metadata=metadata,
        )

        return output_wav_path

    def verify_provenance(self, wav_path: str) -> ProvenanceRecord:
        """Step 4: Inspect any audio file for embedded provenance watermark."""
        return AudioWatermarker.detect_watermark(wav_path)

    def list_enrolled_voices(self) -> List[SpeakerProfile]:
        """List all verified enrolled voice profiles."""
        profiles = []
        if not os.path.exists(self.profiles_dir):
            return []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".json"):
                fpath = os.path.join(self.profiles_dir, filename)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        profiles.append(SpeakerProfile(**json.load(f)))
                except Exception:
                    continue
        return profiles
