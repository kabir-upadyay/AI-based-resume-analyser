# AI Resume Analyzer

A lightweight Flask web app that analyzes student resumes against target job roles using NLP and ML.

## Features
- TF-IDF similarity scoring for role matching
- Skill gap identification from curated role profiles
- Personalized learning roadmap generation
- Secure handling: text-only input, no persistence, length limits

## Run locally

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`.
