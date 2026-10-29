import subprocess
import sys
import os
import tempfile
import pytest

@pytest.fixture
def cli_voices_dir():
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    for f in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, f))
    os.rmdir(tmp_dir)

def test_cli_help():
    res = subprocess.run([sys.executable, "-m", "src.cli", "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "ethical-voice-clone-tts" in res.stdout
    assert "challenge" in res.stdout
    assert "enroll" in res.stdout
    assert "synthesize" in res.stdout
    assert "verify" in res.stdout

def test_cli_challenge():
    res = subprocess.run([sys.executable, "-m", "src.cli", "challenge", "--speaker", "John Doe"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Dynamic Consent Challenge Generated" in res.stdout
    assert "John Doe" in res.stdout

def test_cli_enroll_and_synthesize(cli_voices_dir):
    # 1. Enroll
    transcript = "I authorize Vecesta to clone my voice consent token TESTOK"
    res_enr = subprocess.run(
        [
            sys.executable, "-m", "src.cli", "--dir", cli_voices_dir, "enroll",
            "johnd", "fixtures/sample_audio.wav", "--speaker", "John Doe",
            "--transcript", transcript, "--token", "TESTOK"
        ],
        capture_output=True,
        text=True
    )
    assert res_enr.returncode == 0
    assert "Vocal Consent Verified" in res_enr.stdout

    # 2. List
    res_list = subprocess.run(
        [sys.executable, "-m", "src.cli", "--dir", cli_voices_dir, "list"],
        capture_output=True,
        text=True
    )
    assert res_list.returncode == 0
    assert "johnd" in res_list.stdout

    # 3. Synthesize
    out_wav = os.path.join(cli_voices_dir, "test_out.wav")
    res_syn = subprocess.run(
        [
            sys.executable, "-m", "src.cli", "--dir", cli_voices_dir, "synthesize",
            "johnd", "Hello world from ethical voice", "-o", out_wav
        ],
        capture_output=True,
        text=True
    )
    assert res_syn.returncode == 0
    assert "successfully synthesized" in res_syn.stdout

    # 4. Verify
    res_ver = subprocess.run(
        [sys.executable, "-m", "src.cli", "--dir", cli_voices_dir, "verify", out_wav],
        capture_output=True,
        text=True
    )
    assert res_ver.returncode == 0
    assert "AI PROVENANCE WATERMARK DETECTED" in res_ver.stdout
