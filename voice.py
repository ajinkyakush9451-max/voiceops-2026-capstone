"""Optional Gnani STT/TTS wrapper. Gnani is the only permitted speech provider."""
import os
from pathlib import Path
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient
from .agent import SupportAgent

def process_audio(audio_path: str, output_dir: str = "sample_outputs", language_code: str = "en-IN"):
    if not os.getenv("GNANI_API_KEY"):
        raise RuntimeError("Set GNANI_API_KEY in your environment; do not hardcode it.")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stt, tts = GnaniSTTClient(), GnaniTTSClient()
    agent = SupportAgent()
    heard = stt.transcribe(audio_path, language_code=language_code).get("transcript", "")
    reply = agent.respond(heard) if heard.strip() else "Sorry, I didn't catch that. Could you say it again?"
    stem = Path(audio_path).stem
    (out / f"{stem}.txt").write_text(f"TRANSCRIPT:\n{heard}\n\nREPLY:\n{reply}\n", encoding="utf-8")
    tts.synthesize(reply, voice=os.getenv("GNANI_TTS_VOICE","Kaveri"),
                   model=os.getenv("GNANI_TTS_MODEL","timbre-v2.5"),
                   language=os.getenv("GNANI_TTS_LANGUAGE","en-IN"),
                   output_file=str(out / f"{stem}_reply.wav"))
    return {"transcript": heard, "reply": reply, "audio": str(out / f"{stem}_reply.wav")}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("audio_folder")
    p.add_argument("--output", default="sample_outputs")
    p.add_argument("--language", default="en-IN")
    args = p.parse_args()
    folder = Path(args.audio_folder)
    for audio in sorted(folder.glob("*")):
        if audio.suffix.lower() in {".wav",".mp3",".m4a",".flac"}:
            print(process_audio(str(audio), args.output, args.language))
