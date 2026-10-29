import hashlib
import time
import uuid
from typing import Dict, Optional
from pydantic import BaseModel, Field

class ConsentCertificate(BaseModel):
    """Cryptographic consent certificate confirming authorized voice enrollment."""
    speaker_name: str
    session_token: str
    timestamp: float
    challenge_phrase: str
    audio_sha256: str
    verified: bool
    certificate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ConsentManager:
    """Manages challenge-response consent protocol to prevent non-consensual voice cloning."""

    REQUIRED_KEYWORDS = ("i authorize", "consent", "voice", "vecesta")

    @classmethod
    def generate_challenge(cls, speaker_name: str) -> Dict[str, str]:
        """Generate a randomized, time-limited consent challenge phrase."""
        token = uuid.uuid4().hex[:8].upper()
        now_ts = int(time.time())
        phrase = (
            f"I, {speaker_name}, explicitly authorize and give consent to Vecesta "
            f"to clone and synthesize my voice for personal verification token {token}."
        )
        return {
            "speaker_name": speaker_name,
            "session_token": token,
            "timestamp": str(now_ts),
            "challenge_phrase": phrase,
        }

    @classmethod
    def verify_consent(
        cls,
        audio_bytes: bytes,
        spoken_transcript: str,
        challenge: Dict[str, str]
    ) -> ConsentCertificate:
        """Verify the spoken transcript contains the required consent challenge and keywords."""
        transcript_clean = spoken_transcript.lower().strip()
        phrase_clean = challenge["challenge_phrase"].lower().strip()
        token = challenge["session_token"].lower()

        # Check token and keyword presence
        has_token = token in transcript_clean
        has_keywords = all(kw in transcript_clean for kw in cls.REQUIRED_KEYWORDS)
        
        # Word overlap check
        challenge_words = set(phrase_clean.split())
        spoken_words = set(transcript_clean.split())
        overlap = len(challenge_words.intersection(spoken_words)) / max(1, len(challenge_words))

        is_verified = (has_token and has_keywords) or (overlap >= 0.70)
        if not is_verified:
            raise PermissionError(
                f"Consent verification failed. Spoken transcript does not match the mandatory "
                f"authorization challenge for session token '{challenge['session_token']}'."
            )

        audio_hash = hashlib.sha256(audio_bytes).hexdigest()

        return ConsentCertificate(
            speaker_name=challenge["speaker_name"],
            session_token=challenge["session_token"],
            timestamp=float(challenge["timestamp"]),
            challenge_phrase=challenge["challenge_phrase"],
            audio_sha256=audio_hash,
            verified=True,
        )
