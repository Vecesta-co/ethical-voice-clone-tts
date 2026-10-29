# Contributing to Ethical Voice Clone TTS

Thank you for contributing to responsible, ethical AI!

## Development Setup
```bash
git clone https://github.com/Vecesta-co/ethical-voice-clone-tts
cd ethical-voice-clone-tts
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest --cov=src
```

## Contribution Rules
- All new synthesis features must maintain the provenance watermarking pipeline.
- Voice enrollment must remain strictly gated by the consent protocol.
