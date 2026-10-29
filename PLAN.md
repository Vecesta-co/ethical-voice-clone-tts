# PLAN.md — ethical-voice-clone-tts

## 1. Executive Summary

`ethical-voice-clone-tts` is an open-source, consent-verified voice cloning and text-to-speech (TTS) synthesis engine engineered by Vecesta.co. It enforces cryptographically validated vocal consent verification prior to voice enrollment, embeds imperceptible spread-spectrum audio watermarks into all synthesized waveforms to guarantee provenance and prevent deepfake misuse, and runs locally with a clean NumPy/SciPy acoustic synthesis pipeline.

---

## 2. Competitive Landscape & Reference Analysis

- **Reference**: `coqui-ai/TTS` (MPL 2.0 license).
- **Maintenance & Status**:
  - Coqui closed operations in 2024; the original repo is unmaintained with dozens of broken CUDA/C++ extensions.
  - Zero built-in consent verification — any user can feed stolen audio clips (podcasts, voicemails) and clone anyone's voice without permission.
  - No synthetic provenance watermarking, leaving synthesized clips undetectable from real human speech.
- **How We Are Different & More Capable**:
  1. **Mandatory Dynamic Vocal Consent Protocol**: An enrolled voice requires a signed, time-limited randomized consent phrase. The engine validates that the enrollment audio contains the exact consent pledge.
  2. **Imperceptible Audio Watermarking**: Every synthesized audio file embeds an inaudible high-frequency spread-spectrum watermark containing the speaker ID, generation timestamp, and SHA-256 consent token.
  3. **Standalone Provenance Decoder**: Ships with `aft-verify` / `verify-provenance` CLI to immediately detect whether an audio file was synthesized by this engine and extract the original consent certificate.
  4. **Lightweight & Dependency-Clean**: Pure Python + NumPy/SciPy audio synthesis engine without requiring multi-gigabyte CUDA bloat or abandoned C++ binaries.
  5. **100% Permissive MIT License**: Built from first principles without copying code from Coqui (MPL).

---

## 3. Architecture & Tech Stack

```
           Speaker Voice Sample (.wav) + Dynamic Consent Challenge
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  Consent Verification Gate      │
                    │  - Cryptographic token check    │
                    │  - Dynamic challenge validation │
                    │  - SHA-256 Consent Certificate  │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  Acoustic Embedding Extractor   │
                    │  - MFCC & Mel-energy profiles   │
                    │  - Pitch & Formant contours     │
                    │  - Speaker Profile Persistence  │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
           Input Text ────────► Synthesis Vocoder Engine
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  Spread-Spectrum Watermarker    │
                    │  - Inaudible payload embedding  │
                    │  - Timestamp, Speaker, Hash     │
                    │  - RIFF 'vecs' chunk injection  │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                        Synthesized .WAV Audio File
```

- **Runtime**: Python 3.10+
- **Core Dependencies**: `numpy`, `scipy`, `pydantic`
- **Output Formats**: Standard 16-bit 22,050 Hz / 44,100 Hz mono/stereo PCM `.wav` with embedded RIFF provenance metadata.

---

## 4. File Structure

```
ethical-voice-clone-tts/
├── PLAN.md
├── DEVLOG.md
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── Dockerfile
├── pyproject.toml
├── .gitignore
├── .env.example
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── fixtures/
│   ├── sample_audio.wav
│   └── sample_consent.json
├── src/
│   ├── __init__.py
│   ├── consent.py
│   ├── embedding.py
│   ├── vocoder.py
│   ├── watermarker.py
│   ├── engine.py
│   └── cli.py
└── tests/
    ├── __init__.py
    ├── test_consent.py
    ├── test_embedding.py
    ├── test_vocoder.py
    ├── test_watermarker.py
    ├── test_engine.py
    └── test_cli.py
```
