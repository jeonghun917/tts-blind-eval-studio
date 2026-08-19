# TTS Blind Eval Studio

A tiny CPU-only listening tool for **blind comparison of text-to-speech candidates**.

It is intentionally model-agnostic: no model weights, private datasets, API keys, or GPU are required. Upload WAVs, score candidates under randomized A/B/C labels, then export the ratings and reveal the key only after scoring.

## Current app status

The current `app.py` is the **v1 prototype**. It accepts directly uploaded WAV files named `ITEM__CANDIDATE.wav`.

Because Streamlit's uploader can expose the original filenames, v1 should not be treated as a fully hardened formal blind-testing interface when filenames contain checkpoint identity. The planned v2 flow uses a single ZIP input and never renders internal candidate filenames before reveal.

See [`docs/BLIND_EVAL_STUDIO_V2_SPEC.md`](docs/BLIND_EVAL_STUDIO_V2_SPEC.md).

## Why

TTS development often relies on subjective listening tests, but model/checkpoint names can bias the result. This tool makes a small, reproducible blind-evaluation loop easy to run inside a Lightning Studio.

## v1 input convention

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

Files with the same `ITEM` are grouped into one trial. Candidate names are mapped to A/B/C... labels using a deterministic seed after upload.

## v1 features

- deterministic candidate randomization from a user-provided seed
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

## Research protocol

This repository contains the public methodology for a long-run Matcha-TTS perceptual-scaling study:

- [`docs/RESEARCH_PLAN.md`](docs/RESEARCH_PLAN.md)
- [`docs/EVALUATION_PROTOCOL_V1.md`](docs/EVALUATION_PROTOCOL_V1.md) — fixed 20-prompt primary set + 4 diagnostics and rating anchors
- [`docs/HYPOTHESES_AND_STOPPING_RULE_V1.md`](docs/HYPOTHESES_AND_STOPPING_RULE_V1.md) — falsifiable hypotheses and predeclared stopping rule
- [`docs/ANALYSIS_PLAN_V1.md`](docs/ANALYSIS_PLAN_V1.md) — paired bootstrap, effect sizes, preference analysis, plots
- [`docs/BLIND_EVAL_STUDIO_V2_SPEC.md`](docs/BLIND_EVAL_STUDIO_V2_SPEC.md) — formal evaluator implementation specification
- [`protocols/matcha_scaling_v1.json`](protocols/matcha_scaling_v1.json) — machine-readable frozen-protocol candidate
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
