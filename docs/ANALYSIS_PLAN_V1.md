# Analysis Plan v1

This plan is intentionally simple. The study is small, repeated-measures, and perceptual. The goal is to show the size and uncertainty of checkpoint differences rather than manufacture a significant p-value.

## 1. Unit of comparison

The primary unit is the **prompt** from the fixed 20-prompt primary set.

Every formal checkpoint synthesizes the same prompt IDs. Therefore checkpoint comparisons are paired by prompt.

Diagnostic prompts `X01–X04` are analyzed separately and never pooled into the primary 20-prompt aggregate.

## 2. Primary endpoints

- Overall quality — higher is better
- Artifact Severity — lower is better

Secondary endpoints:

- Naturalness
- Intelligibility
- Rhythm
- Phrase stability
- Ending quality
- Speaker consistency
- artifact-scope tag rates
- pairwise preference rate

The endpoint hierarchy is frozen to reduce cherry-picking.

## 3. What to report for every checkpoint

For every rating dimension:

- number of scored primary prompts
- mean
- median
- interquartile range
- raw per-prompt scores
- 95% bootstrap confidence interval for the mean

For artifact-scope tags:

- count and proportion of `none`
- count and proportion of `broad_texture`
- count and proportion of `local_event`
- count and proportion of `both`

## 4. Paired checkpoint differences

For each prompt, calculate:

`difference = later checkpoint score - earlier checkpoint score`

For Artifact Severity, also show a sign-flipped improvement value for plots:

`artifact improvement = earlier severity - later severity`

This makes positive values mean improvement while preserving the original 1–5 severity scores in the exported data.

Report for each checkpoint pair:

- mean paired difference
- median paired difference
- 95% bootstrap CI of the mean paired difference
- number of prompts improved / tied / worsened
- raw paired differences

## 5. Bootstrap procedure

### One-listener mode

The initial project may use one consistent evaluator. In this case uncertainty is estimated over the fixed prompt sample.

1. Sample 20 primary prompt IDs **with replacement**.
2. Keep the paired checkpoint scores together for each sampled prompt.
3. Calculate the statistic of interest.
4. Repeat 10,000 times.
5. Use the 2.5th and 97.5th percentiles as the 95% bootstrap CI.

Do not independently resample checkpoint A and checkpoint B; that would destroy the pairing.

### Multi-listener mode

If additional listeners are later recruited, preserve listener and prompt structure. Use a two-stage/clustered bootstrap or report listener-level results separately rather than pretending all ratings are independent.

The original one-listener results remain a valid within-listener development study and should not be silently merged with a later multi-listener study.

## 6. Preference analysis

For each prompt-level blind comparison allow:

- earlier checkpoint preferred
- later checkpoint preferred
- tie / no meaningful preference

Report:

- raw counts
- tie rate
- later-checkpoint preference among **non-ties**
- 95% bootstrap CI by resampling prompt IDs

Do not discard the tie rate from the report. A high tie rate is itself evidence that checkpoints are becoming perceptually similar.

## 7. Effect sizes

Use interpretable raw effects first:

- change in points on the 1–5 scale
- percentage-point change in preference
- percentage-point change in artifact-tag prevalence

As a supplementary ordinal-friendly direction measure, report:

`direction effect = (number improved - number worsened) / number non-tied`

Range:

- `+1`: every non-tied prompt improved
- `0`: balanced improvements and regressions
- `-1`: every non-tied prompt worsened

This avoids making the analysis depend on a normal-distribution assumption.

## 8. Category-level analysis

Report the same descriptive summaries separately for:

- short / neutral (`S`)
- phrase boundaries (`P`)
- long form (`L`)
- articulation (`D`)
- endings (`E`)

Category analyses are diagnostic and secondary because each category contains only four primary prompts.

Important examples:

- long-form Overall/Naturalness trend → broad synthetic texture
- phrase-boundary Rhythm/Phrase Stability → prosodic continuity
- articulation Artifact Severity → local phoneme/context problems
- ending Ending Quality → terminal behavior

Do not treat a four-prompt category as a high-powered standalone statistical test.

## 9. Plots

Generate these after unblinding:

1. **Update count vs mean Overall** with 95% bootstrap CI.
2. **Update count vs mean Artifact Severity** with 95% bootstrap CI.
3. Raw prompt points overlaid on checkpoint summaries.
4. Pairwise preference bars including ties.
5. Artifact-scope proportions by checkpoint.
6. Category-level change plot for S/P/L/D/E.

Never plot only the mean without either uncertainty or raw-point context.

## 10. Primary interpretation order

Read results in this order:

1. Overall and Artifact Severity effect size.
2. Bootstrap CI and raw paired differences.
3. Pairwise preference and tie rate.
4. Naturalness and other secondary scales.
5. Category-specific patterns.
6. Free-text artifact notes.

This order is intended to prevent one memorable bad sentence from overriding the aggregate result, while still preserving local-artifact evidence.

## 11. p-values

Formal null-hypothesis p-values are **not primary** for this project.

Reason: the initial prompt set and likely listener count are small, and the practical question is how large and consistent the perceptual change is. Effect sizes, confidence intervals, preference rates, and raw distributions are more informative for the primary development decision.

If a later multi-listener replication is large enough for inferential modeling, that analysis should be declared separately rather than retrofitted onto the original protocol.

## 12. Missing or failed clips

- Never replace a failed difficult clip with an easier one after seeing results.
- Record the failure and reason.
- If synthesis failure makes a prompt unscorable for one checkpoint, exclude that prompt from the paired comparison involving that checkpoint and report the reduced `n`.
- A checkpoint with systematic synthesis failures should be treated as a substantive quality/reliability problem, not merely missing data.