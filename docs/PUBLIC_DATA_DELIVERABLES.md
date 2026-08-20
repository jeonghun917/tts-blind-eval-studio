# Public data deliverables

This study is designed to return more than plots or a prose write-up. Subject to licensing and privacy constraints, the numerical evidence required to re-run the reported analyses will be released in machine-readable form.

## Release principle

The public release should let an independent reader answer three questions without access to the private source speaker corpus or speaker-specific model weights:

1. What was trained, for how long, and at which verified milestone?
2. What did the blinded listener(s) score for each fixed prompt and candidate?
3. Do the published aggregate curves, confidence intervals, effect sizes, and stopping decisions reproduce from the released rows?

The source speech corpus and speaker-specific checkpoints are intentionally outside this release boundary. The derived evaluation data and analysis inputs are not.

## Planned machine-readable datasets

### `data/checkpoint_metrics.csv`

One row per retained checkpoint/milestone.

Planned fields:

- `study_id`
- `speaker_run_id`
- `checkpoint_id`
- `epoch`
- `optimizer_updates`
- `checkpoint_sha256`
- `train_loss` when available
- `val_loss` when available
- `batch_size`
- `sample_rate_hz`
- `vocoder_id`
- `inference_steps`
- `temperature`
- `runtime_gpu_hours`
- `gpu_type`
- `formal_milestone` (`true`/`false`)

### `data/ratings_long.csv`

Primary analysis table. One row per prompt × blind candidate × evaluator.

Planned fields:

- `study_id`
- `protocol_version`
- `session_id`
- `evaluator_id`
- `prompt_id`
- `prompt_category`
- `blind_label`
- `candidate_id_after_reveal`
- `optimizer_updates_after_reveal`
- `overall_quality`
- `naturalness`
- `artifact_severity`
- `intelligibility`
- `rhythm`
- `phrase_stability`
- `ending_quality`
- `speaker_consistency`
- `artifact_scope`
- `completed_primary_trial`

Free-form notes may be omitted or separately redacted if they contain information that would compromise privacy or blinding records.

### `data/preferences.csv`

One row per prompt-level comparison.

Planned fields:

- `study_id`
- `session_id`
- `evaluator_id`
- `prompt_id`
- `candidate_a`
- `candidate_b`
- `preferred_candidate`
- `tie`
- `candidate_a_updates_after_reveal`
- `candidate_b_updates_after_reveal`

### `data/artifact_labels.csv`

Prompt-level artifact-scope observations in a simple analysis-friendly form.

Planned fields:

- `study_id`
- `evaluator_id`
- `prompt_id`
- `checkpoint_id`
- `optimizer_updates`
- `artifact_scope` (`none`, `broad_texture`, `local_event`, `both`)
- `prompt_category`

### `data/paired_differences.csv`

Derived prompt-paired changes between milestone checkpoints.

Planned fields:

- `prompt_id`
- `metric`
- `earlier_checkpoint`
- `later_checkpoint`
- `earlier_updates`
- `later_updates`
- `earlier_score`
- `later_score`
- `signed_improvement`
- `direction` (`improved`, `tied`, `worsened`)

For Artifact Severity, the sign convention will be inverted so positive `signed_improvement` always means perceptual improvement.

### `data/bootstrap_summary.csv`

Reproducible aggregate analysis output.

Planned fields:

- `comparison`
- `metric`
- `n_prompts`
- `point_estimate`
- `median_difference`
- `ci95_low`
- `ci95_high`
- `bootstrap_iterations`
- `bootstrap_unit`
- `effect_size_definition`
- `effect_size`

The preregistered one-listener analysis uses 10,000 paired prompt-bootstrap iterations. Multi-listener analyses, if added later, will use a separately documented clustered/two-stage procedure rather than silently pooling listener rows.

### `data/compute_ledger.csv`

Provider-agnostic accounting for the compute used to produce each milestone.

Planned fields:

- `run_id`
- `segment_id`
- `provider`
- `gpu_type`
- `gpu_count`
- `start_updates`
- `end_updates`
- `updates_completed`
- `paid_runtime_minutes`
- `gpu_hours`
- `updates_per_gpu_hour`
- `interrupted_or_retried`
- `notes`

If a provider permits cost disclosure, a separate `cost` field may be included. The core research analysis will not depend on a provider-specific credit unit.

## Reproducibility artifacts

The release will also include:

- the frozen machine-readable protocol (`protocols/matcha_scaling_v1.json`)
- the human-readable evaluation protocol and rating anchors
- checkpoint/milestone verification rules
- blind randomization and reveal logic
- analysis code that reads the released CSV files and regenerates the primary tables, bootstrap intervals, plots, and stopping-rule classification
- a small synthetic/demo fixture so the analysis pipeline can be tested without the private speech corpus

The target is that the numerical claims in the technical report can be regenerated from the public repository with no hidden spreadsheet steps.

## Prompt selection and anti-cherry-picking

The 20 primary prompts and 4 diagnostic prompts are versioned before the first formal ~300k evaluation. The primary aggregate is defined over the fixed 20-prompt set. Prompts are not added, removed, or replaced after seeing milestone results without creating a new protocol version and separating that analysis from the preregistered primary result.

Failed or missing trials will be recorded. They will not be silently replaced after results are known.

## Release timing

Planned release cadence:

1. Protocol/schema files: before the first formal ~300k evaluation.
2. Milestone metadata and blind-rating rows: after each formal milestone is scored and identity is revealed.
3. Derived paired differences/bootstrap summaries: generated from the released raw rating rows.
4. Final technical report and stopping decision: after the canonical scaling run terminates under the predefined stopping rule.
5. If executed, second-speaker replication tables: released separately with the same schema and a distinct `speaker_run_id`.

## Licensing and privacy boundary

Not publicly redistributed:

- source speaker audio where redistribution is not permitted
- private dataset manifests containing non-public paths or identifiers
- speaker-specific acoustic-model checkpoints
- speaker-specific vocoder weights when redistribution is not permitted
- credentials, secrets, account identifiers, or internal storage paths

Public numerical tables will use neutral study/checkpoint/session identifiers rather than private infrastructure identifiers.

This boundary is intended to preserve licensing and privacy while still releasing the evidence needed to audit the study's statistics and stopping decision.
