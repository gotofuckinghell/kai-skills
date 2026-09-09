---
name: pc-hardware-tuning
description: "PC hardware tuning: DDR5 timings, cooling physics, CPU/GPU."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [hardware, ddr5, timings, memory, cooling, overclocking]
---

# PC Hardware Tuning

Memory overclocking, cooling system physics, hardware tuning.

## Sub-topics

- **DDR5 timing dependency map & calculator logic** → `references/ddr5-timing-reference.md`
- Water cooling pump selection (flow rate physics)

## Key Rules

- Base timing values are in **clock ticks (tCK)**, not nanoseconds. Convert: `ns = ticks × tCK` where `tCK = 2000 / DataRate(MT/s)`.
- tREFI is fixed at 3.9 µs in normal temperature, tRFC scales with die density (16Gb, 24Gb, 32Gb).
- 24Gb M-die has higher tRFC than 16Gb A-die — this is physical, not tunable.
- Dual-rank (DR) requires looser tRRD_L, tFAW, and adds tRDRD_sd/tWRWR_sd.