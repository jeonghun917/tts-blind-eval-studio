# Diagnostic data

This directory contains exploratory or ad-hoc diagnostic measurements collected outside the preregistered formal milestone evaluation.

Rules:

- keep checkpoint IDs, optimizer-update counts, inference constants, seeds, and metric definitions explicit;
- label all such data as descriptive diagnostics, not formal milestone evidence;
- do not merge ad-hoc ratings into the preregistered primary analysis without an explicit protocol amendment;
- objective waveform/mel summary metrics may be stored here, but source audio, private manifests, model weights, and non-redistributable material are excluded;
- blind reveal keys used for unfinished listening sessions are kept outside this public repository until ratings are recorded;
- after a blind diagnostic is completed, anonymized ratings may be joined to checkpoint/seed identities and published here, while preserving any disagreement between initial ad-hoc impressions and later blind reratings.

The first dataset, `cori_d01_e200_e280_seed_sweep_2026-08-20.*`, was created after a severe machine-like artifact was noticed in the D01 phonetic-stress prompt at E280. It compares E200 and E280 across five fixed seeds under the same frozen vocoder and inference settings.

The completed blind rerating is stored in `cori_d01_e200_e280_blind_ratings_2026-08-21.csv`, with a compact paired interpretation in `cori_d01_e200_e280_blind_summary_2026-08-21.json`. This is one-prompt, one-evaluator descriptive evidence and must not be promoted into the formal milestone analysis without a protocol amendment.
