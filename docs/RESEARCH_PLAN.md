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
3. Record checkpoint-level optimizer steps and aggregate perceptual outcomes.
4. Compare the direction and approximate shape of the quality-improvement curve with the primary speaker.
5. Publish aggregate replication findings without redistributing source audio or speaker-specific weights when those materials are not redistributable.

The purpose is external validity: determine whether the primary result is speaker-specific or reflects a broader property of long-run Matcha-TTS training.

## Public outputs

- training/evaluation controller code
- deterministic blind-evaluation app
- versioned evaluation schema and rubrics
- machine-readable fixed protocol
- milestone metadata and aggregate results
- plots/tables of update count versus perceptual outcome
- technical report documenting where continued training stopped paying off
- if executed, aggregate second-speaker replication results and cross-speaker comparison

## Privacy / licensing boundary

The research tooling and aggregate results are intended to be open source. Source speaker audio and speaker-specific model weights are excluded from the public release. Public artifacts must not contain private audio, private checkpoints, secrets, internal identifiers, or licensed material that cannot be redistributed.
