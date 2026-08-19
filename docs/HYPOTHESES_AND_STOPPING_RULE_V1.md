# Hypotheses and Stopping Rule v1

This document turns the long-run Matcha-TTS scaling study into falsifiable statements. It should be frozen before the first formal ~300k evaluation.

## 1. Notation

Let the formal optimizer-update milestones be approximately:

- `u100 = 100k`
- `u300 = 300k`
- `u400 = 400k`
- `u500 = 500k`

For the fixed 20-prompt primary evaluation set, define:

- `Q(u)` = mean Overall-quality score at milestone `u`
- `N(u)` = mean Naturalness score
- `A(u)` = mean Artifact-severity score, where lower is better
- `B(u)` = proportion of clips tagged `broad_texture` or `both`
- `L(u)` = proportion of clips tagged `local_event` or `both`
- `P(a>b)` = proportion of non-tie prompt comparisons preferring checkpoint `a` over checkpoint `b`

The same prompts, vocoder, inference settings, and blind protocol must be used at every milestone.

## 2. Primary hypotheses

### H1 — Diminishing returns in overall quality

The gain from ~100k to ~300k is larger than the gain from ~300k to ~500k:

`Q(u300) - Q(u100) > Q(u500) - Q(u300)`

Expected direction:

`Q(u300) > Q(u100)` and `Q(u500) >= Q(u300)`.

This hypothesis is falsified if the later 300k→500k gain is equal to or larger than the earlier 100k→300k gain, or if later training produces a clear quality regression.

### H2 — Broad synthetic texture declines with training

The prevalence of broad synthetic texture should be non-increasing across formal milestones:

`B(u100) >= B(u300) >= B(u400) >= B(u500)`

A later milestone that produces a clearly higher broad-texture rate counts as a monotonicity violation and must be reported rather than smoothed away.

### H3 — Local artifacts plateau earlier than broad quality

Localized artifacts are expected to improve more slowly after ~300k than before ~300k.

Using the local-artifact tag rate as a simple measure:

`[L(u100) - L(u300)] / 200k > [L(u300) - L(u500)] / 200k`

Equivalent interpretation: the slope of local-artifact improvement becomes smaller in magnitude after ~300k.

A second check uses Artifact Severity on the articulation/ending-sensitive prompts (`D01–D04`, `E01–E04`). If broad Overall/Naturalness improves while those prompt-level local defects remain nearly unchanged, that supports the plateau claim.

## 3. Secondary hypotheses

### H4 — Intelligibility reaches ceiling before naturalness

Because early checkpoints are already mostly intelligible, Intelligibility should change less than Overall/Naturalness across later milestones.

This distinguishes “it can say the words” from “it sounds natural.”

### H5 — Second-speaker replication

If a second-speaker run is executed, the direction of the update-to-quality curve should reproduce qualitatively:

- later training improves broad quality early in the run
- gains diminish at high update counts
- the exact plateau point may differ by speaker/corpus

This is a replication hypothesis, not a claim that both speakers must have identical scores or identical optimal update counts.

## 4. Practical improvement threshold

A raw numerical difference can be statistically nonzero yet too small to matter perceptually. Therefore the study uses a **provisional practical threshold of 0.20 points on a 1–5 rating scale**.

For a later checkpoint versus the previous milestone, treat an interval as showing practical improvement if at least one of the following occurs:

- Overall mean improves by at least `+0.20`
- Naturalness mean improves by at least `+0.20`
- Artifact Severity improves by at least `-0.20`

and the later checkpoint is preferred in more than `55%` of non-tie prompt comparisons.

The 0.20 and 55% thresholds are deliberately simple and must be frozen before the first formal ~300k evaluation. They are not universal scientific constants; they are predeclared decision thresholds for this project.

## 5. No-improvement interval

Call a milestone interval `NO_MEANINGFUL_GAIN` only if **all** of the following hold:

- Overall improvement is `< +0.20`
- Naturalness improvement is `< +0.20`
- Artifact Severity reduction is `< 0.20`
- later-checkpoint preference is `<= 55%` among non-ties
- no major qualitative long-form defect clearly disappears

This deliberately makes the stop decision conservative.

## 6. Stopping rule

Stop extending the canonical scaling run when either:

1. **two successive formal milestone intervals** are classified `NO_MEANINGFUL_GAIN`, or
2. training becomes unstable, checkpoint integrity fails, or a reproducibility/safety gate fails.

Examples:

- 100k→300k: meaningful gain; 300k→400k: no gain → continue to 500k once, because only one no-gain interval exists.
- 100k→300k: no gain; 300k→400k: no gain → stop before 500k.
- 300k→400k: meaningful gain → continuing toward 500k is supported.

Do not continue only because “500k was the original target.”

## 7. Interpretation rule

If broad quality continues to improve but a specific recurring local artifact does not, the default next action is **targeted diagnosis** of data/context/frontend/alignment/prosody rather than simply adding more optimizer updates.

The canonical scaling study must not change architecture, vocoder, post-processing, or frontend to rescue a checkpoint. Those become separate follow-up experiments.