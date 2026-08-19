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

The canonical scaling run does not promote a later checkpoint merely because it is newer.

## Milestones

Primary comparison points:

- ~100k optimizer updates: established early long-form baseline
- ~150k: intermediate checkpoint
- ~300k
- ~400k
- ~500k if the quality-improvement slope remains meaningful

At every major milestone:

1. Verify checkpoint epoch, global optimizer step, and SHA-256.
2. Generate the same long-form evaluation set under the same vocoder and inference settings.
3. Run blinded pairwise or multi-way listening comparisons.
4. Score naturalness, artifact severity, intelligibility, phrase stability, endings, and speaker consistency.
5. Record qualitative recurring artifacts separately from broad synthetic texture.

## Hypotheses

H1: Broad machine-like texture decreases materially between ~100k and ~300k updates.

H2: Improvements continue into the 300k–500k region but with diminishing returns.

H3: Fixed phoneme/context-local artifacts persist longer than broad texture and may plateau even when overall naturalness improves.

H4: If a local artifact remains nearly unchanged while broad quality improves, architecture/data/phoneme-context analysis is more productive than additional blind training.

H5: The broad relationship between optimizer-update count and perceptual improvement should reproduce qualitatively on a second speaker, even if the exact plateau point differs by speaker and corpus.

## Stopping rule

Do not consume compute solely to hit 500k. Stop the canonical scaling run when two successive major milestone comparisons fail to show a meaningful perceptual improvement, or if training becomes unstable.

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
- evaluation schema and rubrics
- milestone metadata and aggregate results
- plots/tables of update count versus perceptual outcome
- technical report documenting where continued training stopped paying off
- if executed, aggregate second-speaker replication results and cross-speaker comparison

## Privacy / licensing boundary

The research tooling and aggregate results are intended to be open source. Source speaker audio and speaker-specific model weights are excluded from the public release. Public artifacts must not contain private audio, private checkpoints, secrets, internal identifiers, or licensed material that cannot be redistributed.
