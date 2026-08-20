# TTS Blind Eval Studio

A tiny CPU-only listening tool for **blind comparison of text-to-speech candidates**.

It is intentionally model-agnostic: no model weights, private datasets, API keys, or GPU are required. Upload a blind-evaluation package, score candidates under randomized A/B/C labels, then export the ratings and reveal the key only after scoring.

## Current app status

The current `app.py` is a **v2 alpha** implementing the first hardening step from the formal evaluator specification: one-ZIP input with internal WAV filenames kept out of the listener-visible interface before reveal.

The ZIP parser validates path safety, rejects unsupported files and duplicate item/candidate pairs, requires at least two candidates per item, enforces consistent candidate membership across items, and parses audio in memory rather than extracting it to a public/static directory.

Protocol-locked rubrics, completion gating, clean long-format exports, bootstrap analysis, plots, and stopping-rule reporting remain planned v2 work.

See [`docs/BLIND_EVAL_STUDIO_V2_SPEC.md`](docs/BLIND_EVAL_STUDIO_V2_SPEC.md).

## Why

TTS development often relies on subjective listening tests, but model/checkpoint names can bias the result. This tool makes a small, reproducible blind-evaluation loop easy to run inside a Lightning Studio or any other Python environment.

## v2-alpha input convention

Upload one ZIP file. Inside the ZIP, name WAV files as:

```text
ITEM__CANDIDATE.wav
```

Example:

```text
S01__candidate_a.wav
S01__candidate_b.wav
S02__candidate_a.wav
S02__candidate_b.wav
```

Files with the same `ITEM` are grouped into one trial. Candidate names are mapped to A/B/C... labels using a deterministic seed after upload. Internal WAV filenames are not rendered to the listener before reveal.

Optional metadata JSON may be included only as `metadata.json` or `candidate_metadata.json`; it is parsed internally and is not displayed during blind scoring.

## Current features

- single-ZIP package input to avoid Streamlit direct-WAV filename leakage
- in-memory ZIP parsing with path-safety validation
- duplicate and candidate-membership validation
- deterministic candidate randomization from a user-provided seed
- any number of trials, 2–26 candidates per trial
- in-browser WAV playback
- overall / naturalness / artifact-severity ratings
- per-candidate notes
- preferred-candidate choice per trial
- CSV export of blind ratings
- explicit post-scoring key reveal and JSON export
- CPU-only, no external service calls

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

The evaluation app itself does not need a paid GPU.

## Research protocol

This repository contains the public methodology for a long-run Matcha-TTS perceptual-scaling study:

- [`docs/RESEARCH_PLAN.md`](docs/RESEARCH_PLAN.md)
- [`docs/EVALUATION_PROTOCOL_V1.md`](docs/EVALUATION_PROTOCOL_V1.md) — fixed 20-prompt primary set + 4 diagnostics and rating anchors
- [`docs/HYPOTHESES_AND_STOPPING_RULE_V1.md`](docs/HYPOTHESES_AND_STOPPING_RULE_V1.md) — falsifiable hypotheses and predeclared stopping rule
- [`docs/ANALYSIS_PLAN_V1.md`](docs/ANALYSIS_PLAN_V1.md) — paired bootstrap, effect sizes, preference analysis, plots
- [`docs/BLIND_EVAL_STUDIO_V2_SPEC.md`](docs/BLIND_EVAL_STUDIO_V2_SPEC.md) — formal evaluator implementation specification
- [`docs/PUBLIC_DATA_DELIVERABLES.md`](docs/PUBLIC_DATA_DELIVERABLES.md) — machine-readable raw/derived data schemas and release boundary
- [`protocols/matcha_scaling_v1.json`](protocols/matcha_scaling_v1.json) — machine-readable frozen-protocol candidate
- [`docs/COMPUTE_BUDGET.md`](docs/COMPUTE_BUDGET.md) — provider-neutral GPU-hour plan based on measured segment throughput
- [`docs/WRITEUP.md`](docs/WRITEUP.md)

## Planned open research outputs

The project is intended to publish enough derived evidence to independently re-run the reported statistics without access to the private speaker corpus or speaker-specific model weights.

Planned machine-readable outputs include prompt-level ratings, pairwise preferences including ties, artifact-scope labels, checkpoint metadata, prompt-paired differences, bootstrap summaries, and a provider-agnostic compute ledger. Analysis code will regenerate the primary plots, intervals, effect sizes, and stopping decision from those released tables.

The fixed protocol and data schemas are defined before the formal high-update evaluations to reduce cherry-picking risk.

Source speaker audio, private dataset manifests/paths, credentials, and speaker-specific model weights are outside the public release when redistribution is not permitted.

## Publishing the evaluator

Before publishing any hosted copy, keep it free of private datasets, checkpoints, credentials, or proprietary audio. A public template should contain only this tool, the protocol, analysis code, and explicitly redistributable demo material.

**Suggested title:** TTS Blind Eval Studio

**Short description:** Reproducible CPU-only blind listening tests for TTS models and checkpoints, with deterministic A/B/C randomization and machine-readable export.

**Tags:** TTS, speech, evaluation, audio, Streamlit, research

## Privacy

Uploaded audio is used by the running Streamlit session for playback and evaluation. ZIP contents are parsed in memory and are not written to a public/static directory by the app. This repository itself contains no uploaded audio and performs no external service calls. Users should still avoid uploading material they are not permitted to process in their chosen environment.

## License

MIT. See `LICENSE`.
