import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import argparse
import os
import time
from colorama import init, Fore, Style
from src.engine import EthicalVoiceEngine

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.MAGENTA}=======================================================
  Ethical Voice Clone TTS (EVC) — Consent-First TTS
  Built by Vecesta.co
======================================================={Style.RESET_ALL}"""
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        prog="ethical-voice-clone-tts",
        description="Consent-verified voice cloning and synthesis engine with inaudible provenance watermarking."
    )
    parser.add_argument("--dir", default="voices", help="Directory storing voice profiles")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Challenge
    p_chal = subparsers.add_parser("challenge", help="Generate a dynamic vocal consent challenge")
    p_chal.add_argument("--speaker", "-s", required=True, help="Full name of voice owner")

    # 2. Enroll
    p_enr = subparsers.add_parser("enroll", help="Enroll a new voice after verifying vocal consent")
    p_enr.add_argument("voice_name", help="Identifier for the new voice")
    p_enr.add_argument("audio", help="Path to consent WAV audio sample")
    p_enr.add_argument("--speaker", "-s", required=True, help="Full name of voice owner")
    p_enr.add_argument("--transcript", "-t", required=True, help="Spoken transcript in the audio")
    p_enr.add_argument("--token", help="Session token from active challenge")

    # 3. Synthesize
    p_syn = subparsers.add_parser("synthesize", help="Synthesize text to speech with watermark")
    p_syn.add_argument("voice_name", help="Identifier of enrolled voice")
    p_syn.add_argument("text", help="Text to speak")
    p_syn.add_argument("--output", "-o", default="output.wav", help="Destination WAV file")
    p_syn.add_argument("--wpm", type=int, default=150, help="Words per minute")

    # 4. Verify
    p_ver = subparsers.add_parser("verify", help="Inspect audio file for provenance watermark")
    p_ver.add_argument("audio", help="Path to WAV audio file to audit")

    # 5. List
    subparsers.add_parser("list", help="List all enrolled voice profiles")

    args = parser.parse_args()
    engine = EthicalVoiceEngine(profiles_dir=args.dir)

    if args.command == "challenge":
        print_banner()
        chal = engine.request_consent_challenge(args.speaker)
        print(f"{Fore.YELLOW}[*] Dynamic Consent Challenge Generated:{Style.RESET_ALL}\n")
        print(f"Speaker:       {chal['speaker_name']}")
        print(f"Session Token: {chal['session_token']}")
        print(f"Timestamp:     {chal['timestamp']}")
        print("\nMandatory Consent Phrase to speak into microphone:")
        print(f"{Fore.CYAN}\"{chal['challenge_phrase']}\"{Style.RESET_ALL}\n")

    elif args.command == "enroll":
        print_banner()
        print(f"{Fore.YELLOW}[*] Enrolling voice '{args.voice_name}' for speaker {args.speaker}...{Style.RESET_ALL}")
        if not os.path.exists(args.audio):
            print(f"{Fore.RED}[✗] Audio file not found: {args.audio}{Style.RESET_ALL}")
            sys.exit(1)

        with open(args.audio, "rb") as f:
            audio_bytes = f.read()

        token = args.token or "MANUAL"
        challenge = {
            "speaker_name": args.speaker,
            "session_token": token,
            "timestamp": str(int(time.time())),
            "challenge_phrase": (
                f"I, {args.speaker}, explicitly authorize and give consent to Vecesta "
                f"to clone and synthesize my voice for personal verification token {token}."
            ),
        }

        try:
            profile = engine.enroll_voice(
                voice_name=args.voice_name,
                audio_bytes=audio_bytes,
                spoken_transcript=args.transcript,
                challenge=challenge,
            )
            print(f"{Fore.GREEN}[✓] Vocal Consent Verified! Certificate ID: {profile.certificate.certificate_id}{Style.RESET_ALL}")
            print(f"    Fundamental Pitch (F0): {profile.pitch_mean:.1f} Hz")
            print(f"    Resonant Formants:      F1={profile.formant_f1:.1f} Hz, F2={profile.formant_f2:.1f} Hz")
            print(f"{Fore.GREEN}[✓] Voice profile saved to {args.dir}/{args.voice_name}.json{Style.RESET_ALL}")
        except PermissionError as e:
            print(f"{Fore.RED}[✗] Consent Rejected: {e}{Style.RESET_ALL}")
            sys.exit(1)

    elif args.command == "synthesize":
        print_banner()
        print(f"{Fore.YELLOW}[*] Synthesizing speech for voice '{args.voice_name}'...{Style.RESET_ALL}")
        print(f"Text: \"{args.text}\"")
        try:
            engine.synthesize(args.voice_name, args.text, args.output, words_per_minute=args.wpm)
            print(f"{Fore.GREEN}[✓] Audio successfully synthesized to {args.output}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[ℹ] Inaudible spread-spectrum provenance watermark injected into audio.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[✗] Synthesis failed: {e}{Style.RESET_ALL}")
            sys.exit(1)

    elif args.command == "verify":
        print_banner()
        print(f"{Fore.YELLOW}[*] Auditing audio provenance for {args.audio}...{Style.RESET_ALL}")
        if not os.path.exists(args.audio):
            print(f"{Fore.RED}[✗] File not found: {args.audio}{Style.RESET_ALL}")
            sys.exit(1)

        rec = engine.verify_provenance(args.audio)
        print("-------------------------------------------------------")
        if rec.watermark_detected:
            print(f"{Fore.GREEN}[✓] AI PROVENANCE WATERMARK DETECTED{Style.RESET_ALL}")
            print(f"Status:        SYNTHETIC AUDIO (AI GENERATED)")
            print(f"Organization:  {rec.organization}")
            print(f"Speaker Name:  {rec.speaker_name}")
            print(f"Consent Token: {rec.consent_token}")
            print(f"Confidence:    {rec.confidence * 100:.1f}%")
        else:
            print(f"{Fore.YELLOW}[ℹ] NO WATERMARK DETECTED{Style.RESET_ALL}")
            print(f"Status: Natural Human Speech or External Unsigned Audio")
        print("-------------------------------------------------------")

    elif args.command == "list":
        print_banner()
        profiles = engine.list_enrolled_voices()
        if not profiles:
            print(f"{Fore.CYAN}No enrolled voices found in '{args.dir}'. Run 'evc challenge' and 'evc enroll'.{Style.RESET_ALL}")
            return
        print(f"{'Voice ID':<16} {'Speaker Name':<20} {'Pitch F0':<12} {'Consent Token'}")
        print("-" * 65)
        for p in profiles:
            print(f"{p.voice_name:<16} {p.speaker_name:<20} {p.pitch_mean:<12.1f} {p.certificate.session_token}")

if __name__ == "__main__":
    main()
