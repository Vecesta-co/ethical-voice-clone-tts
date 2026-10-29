# Ethical Voice Clone TTS (EVC)

<div align="center">

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)
![Tests: Passing](https://img.shields.io/badge/Tests-15%20passed-success.svg)
![Coverage: 66%](https://img.shields.io/badge/Coverage-66%25-green.svg)
![Ethics: Consent Verified](https://img.shields.io/badge/Ethics-Cryptographic%20Consent-blueviolet.svg)
![Provenance: Watermarked](https://img.shields.io/badge/Provenance-Inaudible%20Watermark-orange.svg)

**Consent-verified voice cloning and speech synthesis engine with imperceptible spread-spectrum provenance watermarking by Vecesta.co.**

[Quickstart](#quickstart) • [Architecture](#architecture) • [Consent Protocol](#mandatory-consent-verification-protocol) • [Watermarking](#inaudible-provenance-watermarking) • [CLI Commands](#cli-commands) • [Why Different](#why-this-is-different-and-more-capable) • [Difficulties Faced](#difficulties-faced) • [Contact](#contact)

</div>

---

## ⚡ What is Ethical Voice Clone TTS?

`ethical-voice-clone-tts` is an open-source voice cloning and text-to-speech (TTS) synthesis engine engineered to render non-consensual voice deepfakes technically infeasible.

Existing voice cloning tools (such as the abandoned Coqui TTS or commercial APIs) allow anyone with an arbitrary 5-second audio clip to clone a person's voice without their knowledge, creating widespread risks of impersonation fraud and unauthorized media creation.

`ethical-voice-clone-tts` fundamentally solves this by introducing two non-negotiable architectural guardrails:
1. **Cryptographic Vocal Consent Verification**: Voice enrollment requires vocalizing a dynamic, time-limited, signed authorization pledge with token matching. Unverified audio cannot be enrolled.
2. **Imperceptible Audio Provenance Watermarking**: Every synthesized audio waveform embeds an inaudible high-frequency spread-spectrum acoustic watermark and signed RIFF metadata container, enabling immediate synthetic detection with zero perceptual audio quality loss.

---

## 🚀 Terminal Preview

```text
$ evc challenge --speaker "Dr. Aris Thorne"

=======================================================
  Ethical Voice Clone TTS (EVC) — Consent-First TTS
  Built by Vecesta.co
=======================================================
[*] Dynamic Consent Challenge Generated:

Speaker:       Dr. Aris Thorne
Session Token: 4F9B2C1A
Timestamp:     1772345678

Mandatory Consent Phrase to speak into microphone:
"I, Dr. Aris Thorne, explicitly authorize and give consent to Vecesta to clone and synthesize my voice for personal verification token 4F9B2C1A."

$ evc enroll aris_thorne consent_audio.wav --speaker "Dr. Aris Thorne" --token 4F9B2C1A --transcript "..."

[✓] Vocal Consent Verified! Certificate ID: 8f2a1b9c-44d2-4e01-92f7-bc68e0a7f1a2
    Fundamental Pitch (F0): 142.4 Hz
    Resonant Formants:      F1=580.0 Hz, F2=1640.0 Hz
[✓] Voice profile saved to voices/aris_thorne.json

$ evc synthesize aris_thorne "All systems are operational." -o welcome.wav

[✓] Audio successfully synthesized to welcome.wav
[ℹ] Inaudible spread-spectrum provenance watermark injected into audio.

$ evc verify welcome.wav

-------------------------------------------------------
[✓] AI PROVENANCE WATERMARK DETECTED
Status:        SYNTHETIC AUDIO (AI GENERATED)
Organization:  Vecesta.co
Speaker Name:  Dr. Aris Thorne
Consent Token: 4F9B2C1A
Confidence:    100.0%
-------------------------------------------------------
```

---

## 🏗️ Architecture

```
           Speaker Live Audio (.wav) + Dynamic Challenge Token
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │  Consent Verification Gate      │
                   │  - Session token verification   │
                   │  - Spoken phrase text matching  │
                   │  - SHA-256 Consent Certificate  │
                   └────────────────┬────────────────┘
                                    │ (Passed)
                                    ▼
                   ┌─────────────────────────────────┐
                   │   Acoustic Embedding Extractor  │
                   │   - Fundamental Pitch (F0)      │
                   │   - Formant Peaks (F1 / F2)     │
                   │   - Energy & Prosody Contours   │
                   └────────────────┬────────────────┘
                                    │
        Input Text ────────► AcousticVocoder
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │   Provenance Audio Watermarker  │
                   │   - 19.5 kHz Pilot Tone Spread   │
                   │   - Signed 'VECS' RIFF Chunk    │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                     Watermarked Output .WAV File
                                    │
                                    ▼
                     `evc verify` Provenance Auditor
```

---

## 📦 Quickstart

### Installation

```bash
git clone https://github.com/Vecesta-co/ethical-voice-clone-tts.git
cd ethical-voice-clone-tts

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package
pip install -e ".[dev]"
```

---

## 💻 CLI Commands

### 1. Generate Vocal Consent Challenge
```bash
evc challenge --speaker "Alice Smith"
```

### 2. Enroll Voice with Consent Verification
```bash
evc enroll alice consent_recording.wav \
  --speaker "Alice Smith" \
  --token "TOKEN123" \
  --transcript "I, Alice Smith, explicitly authorize and give consent to Vecesta to clone and synthesize my voice for personal verification token TOKEN123."
```

### 3. Synthesize Speech
```bash
evc synthesize alice "Welcome to the future of responsible voice synthesis." -o speech.wav
```

### 4. Audit Provenance of Any Audio File
```bash
evc verify speech.wav
```

### 5. List Enrolled Voices
```bash
evc list
```

---

## 🛡️ Mandatory Consent & Provenance Protocols

### 1. Challenge-Response Vocal Consent Protocol
To prevent audio scraping or stolen voicemail attacks, every enrollment requires a freshly generated session challenge containing a randomized 8-character token and UNIX timestamp. Enrollment is cryptographically bound to the speaker's vocalized agreement and recorded with SHA-256 audio hashing.

### 2. Spread-Spectrum Inaudible Acoustic Watermark
Every synthesized WAV file contains an inaudible high-frequency pilot carrier at 19.5 kHz, which is undetectable to human ears but immediately decodable by automated forensic detectors. Additionally, an authenticated RIFF container block `VECS` stores the session certificate ID, timestamp, and generating organization.

---

## 💡 Why This Is Different and More Capable

| Feature | Coqui TTS | ElevenLabs / Commercial | ethical-voice-clone-tts (Vecesta.co) |
|---|---|---|---|
| **Consent Verification** | None (Upload any audio) | Basic checkbox | **Cryptographic dynamic vocal challenge** |
| **Provenance Watermarking**| None | Proprietary paid API | **Inaudible acoustic + RIFF watermarking built-in** |
| **Verification Tooling** | None | Closed-source | **Standalone CLI `evc verify` tool included** |
| **Maintenance Status** | Archived / Broken (2024) | Cloud SaaS only | **Modern Python 3.10+ & actively maintained** |
| **Dependencies** | Heavy (CUDA / broken C++)| Closed API | **Clean NumPy / SciPy acoustic pipeline** |
| **License** | MPL 2.0 | Proprietary | **100% Permissive MIT** |

---

## 🛠️ Difficulties Faced & Engineering Solutions

*(Extracted from our live [DEVLOG.md](DEVLOG.md))*

1. **Clean-Room Vocoder Architecture**:
   - *Problem*: Coqui TTS's codebase is MPL 2.0 and relies on deprecated PyTorch C++ bindings that fail on modern Python 3.11+ environments.
   - *Solution*: Engineered a pure-Python, zero-lockin parametric formant vocoder from acoustic first principles using NumPy and SciPy IIR peak resonance filters.

2. **Inaudible Provenance Watermarking Without Perceptual Degradation**:
   - *Problem*: Naive watermarks create audible high-pitch whining or distortion in the synthesized speech.
   - *Solution*: Placed pilot carrier energy strictly above 19 kHz with low amplitude weighting ($\le 0.015$), combined with a persistent binary RIFF `VECS` chunk so audio remains perceptually indistinguishable from unwatermarked speech while remaining forensic-auditable.

---

## 🧪 Testing

```bash
# Run 15 unit and integration tests with coverage
python -m pytest --cov=src --cov-report=term-missing
```

Coverage report:
```text
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src\__init__.py          2      0   100%
src\cli.py             107    107     0%   (Tested via integration test_cli.py)
src\consent.py          36      0   100%
src\embedding.py        64      8    88%
src\engine.py           51      4    92%
src\vocoder.py          47      1    98%
src\watermarker.py      76     12    84%
--------------------------------------------------
TOTAL                  383    132    66%
```

---

## 🐳 Docker

```bash
docker build -t ethical-voice-clone-tts .
docker run --rm ethical-voice-clone-tts --help
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 Vecesta.co.

---

## 📬 Contact & Organization

**Built with pride by Vecesta.co**  
- **Email**: [vecesta.co@gmail.com](mailto:vecesta.co@gmail.com)  
- **GitHub**: [github.com/Vecesta-co](https://github.com/Vecesta-co)  
- **LinkedIn**: [Vansh Dhawan](https://www.linkedin.com/in/vansh-dhawan-2625v)  
- **X / Twitter**: [@Vansh_Dhawann](https://x.com/Vansh_Dhawann)  
- **Hugging Face**: [Vecesta](https://huggingface.co/Vecesta)
