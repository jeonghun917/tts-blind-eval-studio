# Blind Eval Studio v2 — Implementation Specification

Goal: turn the current generic listening app into a protocol-locked research evaluator without exposing checkpoint identity before scoring.

## 1. Problems in v1

The current direct-WAV upload flow can expose filenames such as `ITEM__checkpoint500k.wav` in the Streamlit uploader. That can break blinding before the app replaces candidate names with A/B/C labels.

The current app also allows rating dimensions to exist only as UI code rather than a versioned research protocol, and it does not automatically produce the planned bootstrap summaries or post-reveal plots.

## 2. Input package

### Required v2 input

Upload **one ZIP file**.

Inside the ZIP:

```text
S01__candidate_a.wav
S01__candidate_b.wav
S02__candidate_a.wav
S02__candidate_b.wav
...
```

The browser UI displays only the ZIP filename. Internal WAV filenames must never be rendered before reveal.

Reject:

- path traversal (`../`)
- non-WAV files except optional metadata JSON
- duplicate item/candidate pairs
- items missing a candidate
- candidate count above the supported maximum

Do not extract to a public/static directory. Parse in memory or in a temporary private runtime directory.

## 3. Protocol file

Load a versioned protocol JSON, for example:

`protocols/matcha_scaling_v1.json`

The protocol defines:

- protocol version
- immutable prompt IDs and text
- primary vs diagnostic membership
- category
- required rating dimensions
- 1–5 anchor text
- artifact-scope options
- whether preference allows ties

During a formal run the evaluator must show the protocol version and prevent silent editing of its contents.

## 4. Study metadata

Before scoring, collect:

- `study_id`
- evaluator alias or anonymous listener ID
- protocol version
- blind seed
- optional session note

Do **not** require checkpoint names in listener-visible metadata.

Organizer-only candidate metadata may be stored inside the ZIP or separate reveal key.

## 5. Blinding

Use two deterministic randomizations derived from the seed:

1. candidate-to-label mapping within each prompt
2. prompt presentation order

Candidate labels remain neutral (`A`, `B`, `C`...).

The mapping must not be shown in:

- upload summary
- filenames rendered to UI
- audio-player labels
- browser-visible tables before reveal
- blind-result CSV

## 6. Required scoring fields

For every candidate clip:

- Overall quality, 1–5
- Naturalness, 1–5
- Artifact Severity, 1–5
- Intelligibility, 1–5
- Rhythm, 1–5
- Phrase Stability, 1–5
- Ending Quality, 1–5
- Speaker Consistency, 1–5
- Artifact Scope: `none`, `broad_texture`, `local_event`, `both`
- optional notes

For every prompt comparison:

- preferred candidate
- `tie / no meaningful preference`

The UI should display concise anchor help from the protocol without allowing the listener to modify anchors.

## 7. Completion gate

Before reveal:

- all required primary prompts must have every required score
- every prompt must have a preference/tie choice
- blind results must be exportable

The Reveal section stays disabled until completion or an explicit `incomplete session` export is chosen.

An incomplete session must be marked as incomplete in metadata and cannot silently enter primary analysis.

## 8. Blind exports

### `blind_ratings.csv`

Long format, one row per prompt × blind candidate.

Fields:

- study_id
- protocol_version
- evaluator_id
- item_id
- category
- primary_or_diagnostic
- blind_label
- overall
- naturalness
- artifact_severity
- intelligibility
- rhythm
- phrase_stability
- ending_quality
- speaker_consistency
- artifact_scope
- notes
- preferred
- tie

No checkpoint/candidate identity is included.

### `session_metadata.json`

Contains protocol version, seed hash, timestamp, item counts, completion status, and app version. It must not disclose candidate identity.

## 9. Reveal

After scoring is complete, require a deliberate confirmation:

`I have completed scoring and want to reveal candidate identities.`

Then show/export:

### `reveal_key.json`

Maps:

- item ID
- blind label
- candidate identity
- original internal source filename

The reveal key must remain a separate file from blind ratings.

## 10. Post-reveal automatic analysis

After reveal, merge the blind results with the key **in memory** and generate:

- checkpoint means and medians
- raw prompt distributions
- paired checkpoint differences
- 10,000-resample paired bootstrap 95% CIs
- preference rates and tie rates
- artifact-scope proportions
- category-level summaries

The app should explicitly identify the 20 primary prompts and keep diagnostic prompts separate.

## 11. Post-reveal plots

Generate:

1. optimizer updates vs Overall mean + 95% CI
2. optimizer updates vs Artifact Severity mean + 95% CI
3. raw prompt points by checkpoint
4. preference bars including ties
5. artifact-scope stacked proportions
6. category change plot for S/P/L/D/E

Candidate metadata should provide numeric `optimizer_updates` so the x-axis is numeric rather than inferred from filenames.

## 12. Decision summary

When comparing consecutive formal milestones, the app should compute the preregistered stopping-rule fields:

- Overall mean change
- Naturalness mean change
- Artifact Severity reduction
- later-checkpoint preference among non-ties
- classification: `MEANINGFUL_GAIN` or `NO_MEANINGFUL_GAIN`

The app must show which threshold triggered the decision rather than outputting only the final label.

The app does not autonomously start or stop paid training. It reports the evidence used by the external training controller/human decision.

## 13. Reproducibility

Every export should include:

- app version
- protocol version
- blind-seed hash
- exact prompt IDs
- candidate metadata hash after reveal

A later protocol change must increment the version.

## 14. Privacy boundary

The public repository contains:

- evaluator code
- protocol schema
- generic/fixed evaluation text
- analysis code

It does not contain:

- private speaker audio
- model checkpoints
- training datasets
- Lightning credentials
- nonredistributable evaluation audio

## 15. Implementation order

1. ZIP input and path-safety validation.
2. Protocol JSON loader and frozen rubric UI.
3. Artifact-scope + tie choice.
4. Completion gate and clean blind exports.
5. Reveal key separation.
6. Analysis functions and bootstrap.
7. Plots.
8. Stopping-rule summary.
9. Tests using generated/synthetic WAV fixtures only.