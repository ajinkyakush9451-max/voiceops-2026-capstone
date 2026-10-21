# Dataset completeness status

This is an upload-ready starter repository assembled from files available in the workspace.
It is **not a complete or validated capstone submission**.

## Available
- Python starter agent, run scripts, voice wrapper, requirements, and `.env.example`
- Provided mock tool module
- 5 KB policy documents
- Practice questions and conversations CSVs
- Dataset validator and smoke evaluation script
- Report draft that marks evaluation as pending

## Missing official data
- 7 official CSV files in `data/`
- 16 additional KB Markdown documents (brief requires 21 total; 5 currently available)

## Before submission
1. Extract the official `Capstone_Project_Dataset_FTTT_2026.zip`.
2. Copy the official CSV files into `data/` and all official KB files into `kb/`.
3. Run `python validate_dataset.py` and resolve any errors.
4. Test the agent and Gnani STT/TTS integration with your own voice recording.
5. Record measured evaluation scores and update the report.
6. Never commit `.env` or API keys.
