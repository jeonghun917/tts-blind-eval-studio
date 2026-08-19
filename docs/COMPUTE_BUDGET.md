# Compute budget rationale

Requested support: **75 Lightning credits**.

This is intentionally larger than the bare minimum needed for the remaining canonical training because the research deliverable also includes milestone evaluations, verification overhead, and—if the primary run reaches its stopping rule with budget remaining—a bounded second-speaker replication using the same research protocol.

## Current measured throughput

The existing continuation has been running in 10-epoch L4 segments. A typical segment is approximately 70 minutes and advances about 5,020 optimizer updates at batch size 16.

At the current verified point (~110k optimizer updates), reaching 500k requires roughly 390k additional updates, or about 78 comparable 10-epoch segments. That is roughly 91 L4-hours before retry/validation overhead.

## Proposed allocation

- Long-run canonical training through the supported milestone range: ~44 credits at the currently observed L4 cost/throughput.
- Restart/verification/retry margin: ~7 credits.
- Fixed milestone synthesis and listening-pack generation: ~4 credits.
- Bounded second-speaker replication or, if that cannot be executed, public-data/dataset-independent reproduction validation: up to ~12 credits.
- Contingency for final reproducibility checks and cross-speaker analysis: ~8 credits.

Total ceiling: **75 credits**.

## Second-speaker allocation rule

The replication allocation is not a separate product-training budget. It is used only after the primary scaling run reaches its predefined stopping rule and only to test the same training-duration hypothesis on a separately cleared/licensed speaker corpus. It reuses the same Matcha-TTS architecture, controller, milestone logic, and blind-evaluation methodology.

If insufficient compute remains for a meaningful second-speaker replication, the unused allocation is instead reserved for public-data smoke validation, reproducibility checks, and analysis rather than starting an underpowered unrelated run.

## Spend discipline

The project uses a stopping rule. It will not consume the full allocation merely to reach an arbitrary update count. If two successive major milestone comparisons do not show a meaningful perceptual improvement, the canonical long-run training will stop. Remaining credits will then be used only for the bounded second-speaker replication, public reproduction validation, or final analysis described above.
