# Evaluation Protocol v1 — Matcha-TTS Long-Run Scaling

Status: **freeze candidate**. Once the first formal ~300k evaluation begins, prompt text, scale definitions, and primary/diagnostic membership should not change. Any later change must create a new protocol version and must not be merged into the same primary analysis.

## 1. Purpose

Measure whether perceptual quality improves as optimizer-update count increases while the acoustic architecture, text frontend, vocoder, inference settings, evaluation prompts, and listening procedure remain fixed.

Primary milestone set:

- ~100k optimizer updates
- ~300k
- ~400k
- ~500k if the stopping rule supports continuing

The same prompt IDs and exact text are synthesized at every milestone.

## 2. Fixed prompt set

There are **20 primary prompts** and **4 diagnostic prompts**. The 20 primary prompts enter the main aggregate statistics. The 4 diagnostic prompts are reported separately because they intentionally stress text normalization or unusual forms and can confound acoustic-model quality with frontend behavior.

### A. Short / neutral — primary

| ID | Text |
|---|---|
| S01 | The small lamp beside the window is still on. |
| S02 | I left the blue folder on the kitchen table. |
| S03 | Tomorrow should be warmer than today. |
| S04 | Please close the door before you leave. |

Purpose: expose broad synthetic texture without heavy punctuation or unusually difficult phrasing.

### B. Phrase boundaries / commas — primary

| ID | Text |
|---|---|
| P01 | After the rain stopped, the street grew quiet, and the clouds began to break. |
| P02 | If you have a minute, check the numbers again, then send me the final note. |
| P03 | The package arrived early, but the label was torn, so we opened it carefully. |
| P04 | At the end of the hallway, beyond the glass doors, a narrow staircase leads upstairs. |

Purpose: test pause placement, phrase timing, and stability across multiple prosodic groups.

### C. Long-form continuity — primary

| ID | Text |
|---|---|
| L01 | By the time the train reached the coast, most of the passengers had stopped talking, and the only sounds in the carriage were the wheels, the ventilation system, and an occasional page turning. |
| L02 | The experiment seemed simple at first, but once we repeated it under the same conditions, small differences appeared in the timing, the rhythm, and the way each sentence ended. |
| L03 | Although the forecast had promised clear skies, a thin layer of cloud remained over the city until late afternoon, when the sunlight finally reached the buildings along the river. |
| L04 | When people compare two nearly identical recordings, they often notice broad differences immediately, while smaller pronunciation errors or unstable phrase boundaries become obvious only after repeated listening. |

Purpose: test accumulated synthetic texture, pacing drift, local glitches, and phrase-to-phrase continuity over longer spans.

### D. Articulation / difficult sound sequences — primary

| ID | Text |
|---|---|
| D01 | The sixth street shuttle stopped beside three freshly painted shops. |
| D02 | Bright green glass reflected the crisp spring sunlight. |
| D03 | She carefully measured the rural road's irregular width. |
| D04 | Freshly brewed coffee cooled quickly beside the copper kettle. |

Purpose: stress consonant clusters, liquids, fricatives, and rapid local transitions without turning the set into tongue twisters.

### E. Sentence endings — primary

| ID | Text |
|---|---|
| E01 | That is the result we expected. |
| E02 | I thought the meeting would last longer, but it didn't. |
| E03 | The final value should remain unchanged. |
| E04 | No one noticed the difference until the recording ended. |

Purpose: isolate final-word stability, terminal cadence, cutoff behavior, and end-of-utterance artifacts.

### F. Frontend / normalization stress — diagnostic only

| ID | Text |
|---|---|
| X01 | Flight 407 leaves at 6:45 a.m. |
| X02 | Version 3.2 fixed the issue on the second attempt. |
| X03 | Dr. Rivera reviewed the MRI results before noon. |
| X04 | The file contains 47 samples and 3 missing entries. |

Purpose: observe numbers, abbreviations, acronym handling, and normalization. These clips do **not** enter the main 20-prompt quality aggregate.

## 3. Fixed rating dimensions

All dimensions use a 1–5 integer scale. Do not change anchors between checkpoints.

### Overall quality — primary endpoint

- **1**: unusable or strongly synthetic; major defects dominate
- **2**: poor; clearly synthetic with frequent distracting defects
- **3**: acceptable/intelligible but obviously synthetic
- **4**: good; mostly natural with minor noticeable defects
- **5**: excellent; very natural with only negligible defects

### Naturalness — secondary endpoint

- **1**: highly unnatural
- **2**: clearly unnatural
- **3**: mixed / synthetic but plausible
- **4**: mostly natural
- **5**: convincingly natural

### Artifact severity — co-primary endpoint

Here **lower is better**.

- **1**: no audible artifact
- **2**: faint artifact, easy to ignore
- **3**: clearly audible but not dominant
- **4**: strong and distracting
- **5**: severe; artifact substantially damages the clip

### Intelligibility

- **1**: substantial content cannot be understood
- **2**: several words or phrases unclear
- **3**: mostly understandable with some uncertainty
- **4**: essentially all content clear
- **5**: every word immediately clear

### Rhythm

- **1**: severely unnatural timing/stress
- **2**: frequent timing or stress problems
- **3**: noticeable but tolerable timing issues
- **4**: mostly natural rhythm
- **5**: natural timing and stress throughout

### Phrase stability

- **1**: frequent jumps, collapses, or unstable transitions
- **2**: multiple obvious phrase-level instabilities
- **3**: occasional instability
- **4**: stable except for minor events
- **5**: stable across all phrase boundaries

### Ending quality

- **1**: obvious cutoff, collapse, or strongly unnatural ending
- **2**: clearly flawed ending
- **3**: acceptable but noticeably synthetic ending
- **4**: mostly natural ending
- **5**: clean and natural terminal cadence

### Speaker consistency

- **1**: strong identity/timbre drift
- **2**: repeated noticeable drift
- **3**: some inconsistency
- **4**: mostly stable voice identity
- **5**: stable identity/timbre throughout

## 4. Artifact scope tag

In addition to the sliders, assign exactly one scope label per clip:

- `none`
- `broad_texture` — synthetic/metallic/robotic quality spread over much of the clip
- `local_event` — one or a few localized glitches, warbles, pronunciation failures, or timing events
- `both`

Optional free-text notes may describe the location or type, but the four scope labels above are frozen for analysis.

## 5. Preference choice

For each blind item comparison, select one preferred candidate. Allow an explicit `tie / no meaningful preference` option so the listener is not forced to invent a difference.

## 6. Blind procedure

1. Generate all candidate WAVs using the same vocoder and inference settings.
2. Package them so checkpoint names are not visible to the listener.
3. Randomize candidate labels and trial order deterministically from a stored seed.
4. Score all required dimensions before revealing candidate identity.
5. Export blind ratings before reveal.
6. Reveal the key only after the scoring pass is complete.
7. Keep the reveal key separate from the blind-rating file.

## 7. Interim vs final comparisons

**Interim milestone gate:** compare the previous formal milestone against the current milestone using the full 20-prompt primary set. This is used for the stopping rule.

**Final multi-checkpoint analysis:** compare all retained formal milestones using the same 20 primary prompts. The four diagnostic prompts are summarized separately.

## 8. Protocol integrity

After formal evaluation begins, do not silently:

- rewrite a prompt
- add or remove a primary prompt
- alter a scale anchor
- change whether a metric is primary or secondary
- remove a difficult clip because it hurts a later checkpoint
- change the vocoder or inference settings inside the canonical scaling comparison

Such changes require a new protocol version and separate analysis.