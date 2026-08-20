# Compute budget rationale

This document expresses the remaining research requirement primarily in **GPU-hours and optimizer updates**, not in a provider-specific credit unit. Any grant application should convert this requirement using the target provider's current instance pricing and a short compatibility benchmark before committing to a long run.

## Current verified point

The latest retained canonical checkpoint used for planning is approximately:

- **140,560 optimizer updates**
- batch size 16
- about **5,020 optimizer updates per 10 epochs**

Training is paused rather than extending the run simply to consume the remaining self-funded balance.

## Measured recent throughput

Recent successful 10-epoch segments on a 24 GB L4-class GPU completed in approximately **50–56 minutes of paid job runtime** and advanced about **5,020 optimizer updates** each.

Across six recent successful segments, mean paid runtime was approximately **53.5 minutes per 5,020 optimizer updates**, corresponding to roughly **5.6k optimizer updates per GPU-hour** on that environment.

This measured rate is a planning baseline, not an assumption that a different GPU/provider will have identical throughput. A grant-funded environment should first run one bounded 10-epoch benchmark segment and update the estimate from measured `updates_per_gpu_hour`.

## Remaining canonical-run estimate

From 140,560 updates:

### To ~400k

- remaining updates: ~259,440
- equivalent 10-epoch segments at the current recipe: ~51.7
- L4-class baseline compute at 53.5 min/segment: **~46 GPU-hours**

### To ~500k

- remaining updates: ~359,440
- equivalent 10-epoch segments at the current recipe: ~71.6
- L4-class baseline compute at 53.5 min/segment: **~64 GPU-hours**

### Operational margin

A 15% margin for environment validation, checkpoint verification, occasional interruption/retry, milestone synthesis, and final reproducibility checks gives a planning ceiling of roughly **73 GPU-hours** for the remaining primary scaling run through ~500k.

The stopping rule may terminate the run earlier. The project will not consume the ceiling merely because compute is available.

## Optional second-speaker replication

The second-speaker experiment is conditional and lower priority than the primary scaling run.

It begins only if:

1. the primary run reaches its predefined stopping decision;
2. sufficient grant compute remains for a meaningful bounded replication;
3. the second corpus is separately cleared/licensed; and
4. the same Matcha-TTS recipe and evaluation protocol can be applied without changing the research question.

A provider-specific request should therefore separate:

- **primary requirement:** enough compute to complete the canonical milestone/stopping-rule study;
- **optional stretch allocation:** a bounded second-speaker replication using the same protocol.

If the remaining award is too small for a meaningful replication, it should instead be used for reproducibility validation, analysis, or left unused rather than starting an underpowered unrelated experiment.

## Provider conversion example

The public research requirement is deliberately stated as GPU-hours. For a provider offering a compatible 24–48 GB single-GPU instance, the application can estimate monetary support as:

`estimated grant cost = benchmarked GPU-hours × current provider hourly price`

For example, if the target environment reproduces the current ~64 GPU-hour primary estimate and costs approximately $1–$2 per GPU-hour, the direct primary training component is on the order of tens to low hundreds of dollars, before any optional replication or faster/more expensive hardware choice.

The application should not inflate the request to the program maximum. It should ask for enough compute to answer the declared research question, with a clearly separated stretch allocation if the program prefers awarding larger fixed credit blocks.

## Compute ledger

Every paid segment used in the final study will be recorded in the planned public `data/compute_ledger.csv` with:

- provider and GPU type
- start/end optimizer updates
- paid runtime
- GPU-hours
- updates per GPU-hour
- interruption/retry marker

This makes the final quality-vs-compute curve auditable and lets future users translate the result to other hardware or cloud providers without relying on a proprietary credit unit.
