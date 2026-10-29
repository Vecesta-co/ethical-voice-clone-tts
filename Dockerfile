FROM python:3.11-slim

LABEL maintainer="vecesta.co@gmail.com"
LABEL description="Ethical Voice Clone TTS — Consent-verified TTS by Vecesta.co"

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/
COPY fixtures/ ./fixtures/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["ethical-voice-clone-tts"]
CMD ["--help"]
