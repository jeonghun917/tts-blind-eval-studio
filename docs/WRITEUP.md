# Why I stopped comparing TTS checkpoints by filename

When a text-to-speech model is trained for a long time, evaluating progress sounds simple: synthesize the same sentence from two checkpoints and choose the better one.

The problem is that checkpoint names already tell you what you are supposed to hear. If one file is called `100k.wav` and the other is `500k.wav`, it is difficult to know whether the later model actually sounds better or whether the label is influencing the decision.

I started treating listening tests more like small experiments.

## Keep the listening set fixed

Use the same held-out sentences when comparing checkpoints. That makes improvements and regressions easier to notice across training runs, especially for recurring issues such as pronunciation artifacts, sentence endings, rhythm, or long-sentence stability.

## Hide checkpoint identity

For every sentence, map model names to neutral labels such as A, B, and C. Keep the mapping separate from the ratings until the listening pass is complete.

This is not a substitute for a formal MOS study, but it removes an obvious source of bias from day-to-day model development.

## Keep the reveal key separate

The evaluator should produce two outputs:

- blind ratings, which contain only item IDs and neutral candidate labels
- a reveal key, which maps those labels back to the original model/checkpoint names

That separation makes it harder to accidentally unblind the experiment while scoring.

## Make the tool model-agnostic

The listening evaluator does not need to know anything about the acoustic model, vocoder, dataset, or training framework. Its input is simply WAV files named with an item and candidate identifier.

That means the same evaluator can compare:

- different checkpoints of one TTS model
- different vocoders
- different inference settings
- a model against a reference recording
- completely different TTS systems

## Why put it in a Lightning Studio

Publishing the evaluator as a small CPU-only Studio makes the evaluation environment reproducible too: someone can duplicate it, upload their own WAVs, and run the same workflow without installing a local stack.

The public tool intentionally contains no model weights, private audio, datasets, or credentials. It is just the reusable evaluation layer.

## TTS Blind Eval Studio

The tool provides deterministic A/B/C randomization from a seed, in-browser audio playback, overall/naturalness/artifact ratings, notes, a preferred-candidate choice, CSV export, and a separately gated JSON reveal key.

GitHub: https://github.com/jeonghun917/tts-blind-eval-studio

Lightning Community Studio: to be added after publication.
