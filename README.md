# VoiceOps 2026 — ZentroMart AI Customer Support Agent

An educational capstone implementation for document-grounded customer support with conversational context, mock order verification, ticket escalation, and optional Gnani speech input/output.

## Important dataset note
The files available when this package was assembled included five knowledge-base Markdown documents and the two practice CSVs, but not all nine data CSVs and all 21 KB documents. Download the official `Capstone_Project_Dataset_FTTT_2026.zip` from the capstone page and extract it. Copy all current `kb/*.md` files into this repository's `kb/`, and the complete `data/*.csv` files into `data/`. Keep the supplied `tools.py` in `tools/`; it expects `data/` one directory above `tools/`. Do not use the superseded policy as current policy evidence.

## Setup
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set environment variables in your shell or a local `.env` loader of your choice. Never commit `.env` or keys. `OPENAI_API_KEY` is optional for lexical fallback; `GNANI_API_KEY` is required for voice processing.

## Run the text agent
```bash
python run.py
```

## Run audio batch (Gnani STT/TTS only)
```bash
python run_audio.py path/to/audio_folder --output sample_outputs --language en-IN
```
Supported audio extensions in this wrapper: WAV, MP3, M4A, FLAC. Check the current Gnani SDK documentation for accepted formats, model names and response schema.

## Validate the official dataset
Place the official dataset structure in the expected locations, then run:
```bash
python validate_dataset.py
```
The validator expects all CSVs and all 21 KB documents from the official dataset.

## Design
- Lexical section retrieval preserves section IDs and policy metadata.
- Superseded policies are down-weighted; current documents are preferred.
- LLM answers receive retrieved excerpts and a grounding system prompt.
- Order details are gated behind phone-last-four or delivery-pincode verification via the supplied mock tool.
- Ticket success is reported only when `create_ticket` returns `created=True`.
- Gnani is used for STT and TTS; no other speech provider is implemented.

## Known limitations / before final submission
This is a starter implementation and must be tested against the complete official dataset. The simple lexical retriever is a baseline, not a semantic vector database. Add evaluation for every practice question and conversation, validate policy/date edge cases, verify the installed Gnani SDK signatures, and record actual Step 1 vs Step 2 scores. The current report intentionally does not claim unrun scores. The supplied mock tool is educational, not production authentication.


## Dataset completeness status

See [`DATASET_STATUS.md`](DATASET_STATUS.md). This package is a starter and is not fully validated. The official dataset is incomplete: only five of the required 21 KB documents and none of the seven official CSV tables were available when packaged. Do not submit as complete until you add the original dataset and run the validator. Keep secrets out of GitHub; upload `.env.example`, never `.env`.
