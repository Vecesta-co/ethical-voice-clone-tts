# DEVLOG.md — ethical-voice-clone-tts

## Engineering Log & Challenges Solved

### Milestone 1: Ethical Voice Cloning Architecture & Consent Protocol
- **Date**: 2026-10-29
- **Goal**: Build a consent-first voice cloning and TTS engine that renders deepfake misuse technically infeasible through cryptographic consent verification and inaudible watermarking.

---

### Obstacle 1: Coqui TTS Maintenance & License Restrictions
- **Problem**: `coqui-ai/TTS` is governed by the Mozilla Public License (MPL 2.0), has been abandoned since early 2024, and suffers from severe dependency rot (requiring legacy PyTorch/CUDA wheels and broken setup.py builds).
- **Solution**: Engineered an independent, clean-room acoustic synthesis architecture from first principles using standard Python, NumPy, SciPy, and RIFF chunk parsing. Released under permissive MIT license.

---

### Obstacle 2: Imperceptible Audio Watermarking Resilience
- **Problem**: Naive metadata tags in audio files (like ID3 or RIFF INFO tags) are instantly wiped when audio is stripped or converted to raw PCM arrays.
- **Solution**: Designed a two-layer provenance watermarking system:
  1. *Acoustic Layer*: Encodes a high-frequency (18.5 kHz–20 kHz) phase-modulated spread-spectrum bitstream directly into the audio waveform samples.
  2. *Container Layer*: Injects an authenticated `vecs` RIFF chunk with digital signature into the WAV header.
  The provenance decoder can reconstruct authenticity from either the audio samples or the container header.

---

### Obstacle 3: Dynamic Consent Challenge Formulation
- **Problem**: Pre-recorded phrases or static consent agreements can be replayed or spliced.
- **Solution**: Created a challenge-response protocol where the consent generator produces a short session UUID and timestamped hash that the user must vocalize. Enrollment fails if the transcript does not match the active session challenge.
