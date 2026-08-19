# TTS Blind Eval Studio

A tiny CPU-only listening tool for **blind comparison of text-to-speech candidates**.

It is intentionally model-agnostic: no model weights, private datasets, API keys, or GPU are required. Upload WAVs, score candidates under randomized A/B/C labels, then export the ratings and reveal the key only after scoring.

## Why

TTS development often relies on subjective listening tests, but model/checkpoint names can bias the result. This tool makes a small, reproducible blind-evaluation loop easy to run inside a Lightning Studio.

## Input convention

Name WAV files as:

```text
ITEM__CANDIDATE.wav
```

Example:

```text
sentence01__reference.wav
sentence01__baseline.wav
sentence01__checkpoint500k.wav
sentence02__reference.wav
sentence02__baseline.wav
sentence02__checkpoint500k.wav
```

Files with the same `ITEM` are grouped into one blind trial. Candidate names are hidden behind A/B/C... labels using a deterministic seed.

## Features

- deterministic blind randomization from a user-provided seed
- any number of trials, 2–26 candidates per trial
- in-browser WAV playback
- overall / naturalness / artifact-severity ratings
- per-candidate notes
- preferred-candidate choice per trial
- CSV export of blind ratings
- explicit post-scoring key reveal and JSON export
- CPU-only, no external service calls

## Run locally or in Lightning Studio

```bash
python -m pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

In a Lightning Studio, use a CPU workspace for setup and runtime; this app does not need a paid GPU.

## Research context

This repository also contains the public methodology for a long-run Matcha-TTS perceptual-scaling study:

- [`docs/RESEARCH_PLAN.md`](docs/RESEARCH_PLAN.md)
- [`docs/COMPUTE_BUDGET.md`](docs/COMPUTE_BUDGET.md)
- [`docs/WRITEUP.md`](docs/WRITEUP.md)

Open-source deliverables are the evaluation tooling, methodology, experiment configuration, and aggregate findings. Source speaker audio and speaker-specific model weights are not part of this public repository.

## Publishing to the Lightning Community

Before publishing a Studio, keep it free of private datasets, checkpoints, credentials, or proprietary audio. The public template should contain only this tool and any explicitly redistributable demo material.

**Suggested title:** TTS Blind Eval Studio

**Short description:** Reproducible CPU-only blind listening tests for TTS models and checkpoints, with deterministic A/B/C randomization and CSV/JSON export.

**Tags:** TTS, speech, evaluation, audio, Streamlit, research

## Privacy

Uploaded audio is used by the running Streamlit session for playback and evaluation. This repository itself contains no uploaded audio and performs no external API calls. Users should still avoid uploading material they are not permitted to process in their chosen environment.

## License

MIT. See `LICENSE`.
