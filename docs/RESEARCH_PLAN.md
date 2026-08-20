# Research plan: Matcha-TTS long-run perceptual scaling

## Question

When a fixed single-speaker Matcha-TTS recipe remains intelligible but still sounds synthetic in long-form listening, how much of that residual artifact is reduced by additional optimizer updates alone?

A secondary replication question is included if compute remains after the primary run reaches its stopping rule: does the observed update-to-quality curve reproduce on a second speaker when the same Matcha-TTS training and evaluation protocol is reused?

## Experimental constants

Keep fixed across milestone checkpoints:

- acoustic architecture and frontend
- sample rate / mel configuration
- training corpus and split within each speaker run
- batch size and optimizer recipe unless a later ablation is explicitly separated from the main run
- neural vocoder
- inference temperature and ODE steps
- evaluation prompts
- blind listening procedure
- rating definitions and primary/secondary endpoint roles

The canonical scaling run does not promote a later checkpoint merely because it is newer.

## Formal milestones

Primary formal comparison points:

- ~100k optimizer updates: established early long-form baseline
- ~300k
- ~400k
- ~500k if the stopping rule supports continuing

An available ~150k checkpoint may be retained as an **intermediate descriptive checkpoint**, but the preregistered main hypotheses use 100k/300k/400k/500k so that the primary comparisons remain simple and fixed.

At every formal milestone:

1. Verify checkpoint epoch, global optimizer step, and SHA-256.
2. Generate the exact same protocol-locked evaluation set under the same vocoder and inference settings.
3. Run blinded pairwise or multi-way listening comparisons.
4. Score the frozen rating dimensions.
5. Record artifact scope (`none`, `broad_texture`, `local_event`, `both`) plus optional notes.
6. Export blind results before revealing checkpoint identity.
7. Run the preregistered paired analysis and stopping-rule summary after reveal.

## Protocol documents

The detailed study design is versioned separately so it can be frozen before formal evaluation:

- [`EVALUATION_PROTOCOL_V1.md`](EVALUATION_PROTOCOL_V1.md)
- [`HYPOTHESES_AND_STOPPING_RULE_V1.md`](HYPOTHESES_AND_STOPPING_RULE_V1.md)
- [`ANALYSIS_PLAN_V1.md`](ANALYSIS_PLAN_V1.md)
- [`BLIND_EVAL_STUDIO_V2_SPEC.md`](BLIND_EVAL_STUDIO_V2_SPEC.md)
- [`PUBLIC_DATA_DELIVERABLES.md`](PUBLIC_DATA_DELIVERABLES.md)
- machine-readable protocol: [`../protocols/matcha_scaling_v1.json`](../protocols/matcha_scaling_v1.json)

Once the first formal ~300k evaluation begins, prompt text, rating anchors, endpoint roles, and decision thresholds should not be silently changed.

## Hypotheses

H1: Overall perceptual gain from ~100k to ~300k is larger than the gain from ~300k to ~500k.

H2: Broad synthetic texture prevalence declines monotonically or near-monotonically across formal milestones.

H3: Fixed phoneme/context-local artifacts improve more slowly after ~300k and may plateau even when broad quality continues to improve.

H4: Intelligibility reaches ceiling earlier than naturalness, so late training mainly improves perceptual quality rather than basic comprehensibility.

H5: The broad relationship between optimizer-update count and perceptual improvement should reproduce qualitatively on a second speaker, even if the exact plateau point differs by speaker and corpus.

Exact operational definitions and falsification criteria are in `HYPOTHESES_AND_STOPPING_RULE_V1.md`.

## Stopping rule

Do not consume compute solely to hit 500k. Use the predeclared practical-improvement thresholds and stop when two successive formal milestone intervals are classified as showing no meaningful gain, or if training/integrity becomes unstable.

Only after the primary run reaches that stopping rule, and only if allocated compute remains, begin the second-speaker replication. The replication is bounded to the same research question and does not expand into unrelated architecture or product work.

## Secondary-speaker replication

If budget remains:

1. Use a separately cleared/licensed speaker corpus.
2. Reuse the same Matcha-TTS architecture, frontend, optimizer family, milestone logic, checkpoint verification, and blind-evaluation tooling.
3. Record checkpoint-level optimizer steps and prompt-level perceptual outcomes using the same public data schema.
4. Compare the direction and approximate shape of the quality-improvement curve with the primary speaker.
5. Publish derived replication data and cross-speaker analysis without redistributing source audio or speaker-specific weights when those materials are not redistributable.

The purpose is external validity: determine whether the primary result is speaker-specific or reflects a broader property of long-run Matcha-TTS training.

## Public research data release

The project will release the numerical evidence required to re-run the reported analysis, not only aggregate plots.

Planned machine-readable outputs include:

- `checkpoint_metrics.csv`: verified milestone metadata, optimizer updates, runtime/GPU metadata, and available losses
- `ratings_long.csv`: prompt × checkpoint × evaluator raw rating rows for the frozen dimensions
- `preferences.csv`: prompt-level pairwise preferences including explicit ties
- `artifact_labels.csv`: broad/local artifact-scope labels by prompt and milestone
- `paired_differences.csv`: raw prompt-paired checkpoint changes
- `bootstrap_summary.csv`: point estimates, 95% intervals, and effect-size summaries generated from the released rows
- `compute_ledger.csv`: provider-agnostic GPU-hours, update throughput, retries/interruption markers, and milestone accounting
- versioned protocol/schema files plus analysis code that regenerates the primary tables, plots, bootstrap intervals, and stopping classification

The detailed schemas and release boundary are frozen in [`PUBLIC_DATA_DELIVERABLES.md`](PUBLIC_DATA_DELIVERABLES.md).

The fixed 20-prompt primary set is the unit of the preregistered aggregate analysis. Prompts will not be removed or replaced after seeing milestone results unless the protocol is versioned and the changed analysis is reported separately. Missing or failed trials will be recorded rather than silently substituted.

## Reproducibility target

An independent reader should be able to use the public repository, without access to the private speaker corpus or model weights, to:

1. verify which milestone/update counts were compared;
2. inspect the raw prompt-level blinded scores and preferences after reveal;
3. recompute checkpoint means, paired differences, artifact-scope proportions, and preference rates;
4. re-run the declared 10,000-iteration paired prompt bootstrap for the one-listener primary analysis;
5. regenerate the primary plots and tables; and
6. reproduce the declared stopping-rule classification from the released numerical data.

A small synthetic/demo fixture will be provided so the evaluation-analysis pipeline can be smoke-tested without private audio.

## Public outputs

- restart-safe training/evaluation controller pattern
- deterministic blind-evaluation app
- versioned evaluation schema and rubrics
- machine-readable fixed protocol
- machine-readable prompt-level ratings, preferences, artifact labels, paired differences, and bootstrap summaries
- milestone metadata and provider-agnostic compute ledger
- plots/tables of update count versus perceptual outcome with uncertainty and raw prompt context
- analysis code sufficient to regenerate the reported numerical results from the released tables
- technical report documenting where continued training stopped paying off
- dataset-independent reproduction guide
- if executed, second-speaker derived data and cross-speaker comparison using the same schema

## Privacy / licensing boundary

The research tooling, protocol, derived numerical data, and analysis results are intended to be open source. Source speaker audio and speaker-specific model weights are excluded from the public release when redistribution is not permitted.

Public artifacts must not contain private audio, private checkpoints, secrets, private dataset paths/manifests, account identifiers, or licensed material that cannot be redistributed. Neutral study/checkpoint/session identifiers will be used in released numerical tables.

This boundary is designed to preserve licensing and privacy while still exposing enough data to audit the study's statistics, effect sizes, and stopping decision.
