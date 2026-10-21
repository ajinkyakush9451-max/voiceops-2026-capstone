#!/usr/bin/env python3
"""Batch process a folder of audio files with Gnani STT/TTS."""
from src.voice import process_audio
import argparse
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("audio_folder")
p.add_argument("--output", default="sample_outputs")
p.add_argument("--language", default="en-IN")
a=p.parse_args()
for f in sorted(Path(a.audio_folder).glob("*")):
    if f.suffix.lower() in {".wav",".mp3",".m4a",".flac"}:
        print(process_audio(str(f), a.output, a.language))
