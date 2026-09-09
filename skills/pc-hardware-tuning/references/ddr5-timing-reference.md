# DDR5 Timing Reference — JEDEC Dependency Map

## Clock Conversion

```
tCK (ns) = 2000 / DataRate (MT/s)
t (ns)   = ticks × tCK
t (ticks)= t (ns) / tCK
```

| Frequency | tCK (ns) |
|-----------|----------|
| DDR5-4800 | 0.417 |
| DDR5-5600 | 0.357 |
| DDR5-6000 | 0.333 |
| DDR5-6400 | 0.3125 |
| DDR5-8000 | 0.250 |

---

## Group 1 — Primary timings (independent, set by chip vendor)

These are the "passport" of the chip. Not computed — set directly.

| Timing | Meaning | Typical 6000 MT/s |
|--------|---------|-------------------|
| **tCL** | CAS Latency — delay to first word of data | 30–36 |
| **tRCD** | RAS→CAS: activate row → read/write | 36–40 |
| **tRP** | Row Precharge: close row | 36–40 |

---

## Group 2 — Derived from primaries (JEDEC formulas)

| Timing | Formula | Typical 6000 DR |
|--------|---------|-----------------|
| **tRAS** | ≥ tRCD(RD) + tRTP | 76 (tRCD=40, tRTP=12, +safety margin) |
| **tRC** | = tRAS + tRP | 116 |
| **tCWL** | ≈ tCL − 2 | 28 |
| **tRTP** | ≥ 12 tCK (min) | 12 |

---

## Group 3 — tRRD / tFAW family (inter-row activate)

| Timing | Formula | SR | DR |
|--------|---------|-----|-----|
| **tRRD_S** | base (same bank group) | 4 | 4 |
| **tRRD_L** | ≈ 2× tRRD_S (different bank group) | 8 | **12** |
| **tFAW** | = 4× tRRD_S (window for 4 activates) | 16 | **32** |

tFAW limits total activation rate across 4 bank groups.

---

## Group 4 — tWR / tWTR family (write → read)

| Timing | Formula | Typical |
|--------|---------|---------|
| **tWR** | multiple of 6 (DDR5 rule) | 48 |
| **tWTR_S** | base (different bank group) | 4 |
| **tWTR_L** | = 2× tWTR_S (same bank group) | 16 |

---

## Group 5 — Refresh (critical for 24Gb M-die)

| Timing | What | Dependency |
|--------|------|-----------|
| **tREFI** | Interval between refresh | Fixed 3.9 µs (normal temp) |
| **tRFC** | Refresh duration | **Scales with die density** |
| **tRFC2** | Fine granularity refresh | ≈ tRFC / 2 |
| **tRFCsb** | Same-bank refresh | ≈ tRFC / 4 |

### tRFC by die density (nanoseconds)

| Density | tRFC (ns) | tRFC in ticks @6000 |
|---------|-----------|---------------------|
| 8 Gb | ~195 | ~585 |
| 16 Gb (A-die) | ~295 | ~885 |
| **24 Gb (M-die)** | **~350** | **~1050** |
| 32 Gb | ~410 | ~1230 |

**This is the key reason 24Gb M-die cannot match A-die tRFC values** — physically more cells to refresh.

---

## Group 6 — Column-to-column

| Timing | Formula | Typical |
|--------|---------|---------|
| **tCCD_S** | base (same bank group) | 4 |
| **tCCD_L** | = 2× tCCD_S (different bank group) | 8 |

---

## Group 7 — Dual-Rank specific (only for 2×32GB / 2×48GB)

| Timing | Meaning | Typical (DR) |
|--------|---------|--------------|
| **tRDRD_sd** | read→read, different rank | 6 |
| **tWRWR_sd** | write→write, different rank | 6 |

These do not exist on single-rank (value = 1 on Auto).

---

## Full dependency graph

```
INDEPENDENT (chip passport):
    tCL, tRCD, tRP

        ├──→ tRAS = tRCD + tRTP
        │        └──→ tRC = tRAS + tRP
        │
        ├──→ tCWL = tCL − 2
        │
        └──→ tRTP (min 12)

DIE PHYSICS (density → refresh):
    density (Gb) ──→ tRFC ──→ tRFC2 = tRFC/2
                     │         └──→ tRFCsb = tRFC/4
                     └──→ tREFI (fixed 3.9 µs)

INTER-ROW (bank groups):
    tRRD_S ──→ tRRD_L = 2 × tRRD_S
       └─────→ tFAW = 4 × tRRD_S

WRITE→READ:
    tWTR_S ──→ tWTR_L = 2 × tWTR_S
    tWR (multiple of 6)

COLUMNS:
    tCCD_S ──→ tCCD_L = 2 × tCCD_S

DUAL-RANK:
    tRDRD_sd, tWRWR_sd (only DR, typically = 6)
```

---

## Calculator construction order

1. **Inputs:** DataRate, tCL, tRCD, tRP, die density (16/24/32 Gb), rank count (SR/DR)
2. **Compute tCK** = 2000 / DataRate
3. **Refresh block:** lookup tRFC (ns) by density → convert to ticks → tRFC2/4 = division
4. **Derived primaries:** tRAS = tRCD + tRTP, tRC = tRAS + tRP
5. **Bank groups:** tRRD_S → tRRD_L (×2) → tFAW (×4)
6. **Write:** tWR (multiple of 6), tWTR_S → tWTR_L (×2)
7. **Columns:** tCCD_S → tCCD_L (×2)
8. **DR corrections:** if dual-rank → raise tRRD_L to 12, tFAW to 32, add tRDRD_sd/tWRWR_sd = 6

---

## Example: 2×48GB Hynix 24Gb M-die, DR, 6000 MT/s

```
tCK = 2000 / 6000 = 0.333 ns

Primary:   tCL=30, tRCD=40, tRP=40
Refresh:   tRFC ≈ 500 ticks (24Gb), tREFI = 11700 ticks (~3.9 µs)
Derived:   tRAS=76, tRC=116, tRTP=12
RRD/FAW:   tRRD_S=4, tRRD_L=12 (DR), tFAW=32 (DR)
Write:     tWR=48, tWTR_S=4, tWTR_L=16
Columns:   tCCD_S=4, tCCD_L=8
DR specific: tRDRD_sd=6, tWRWR_sd=6

Voltages:  VDD=1.35, VDDQ=1.35, VDDIO=1.35, SOC=1.20
```

---

## Existing public calculators (no full dependency calculator exists)

| Tool | URL | What it does |
|------|-----|--------------|
| Alphadev RAM Timing Simulator | ram.alphadev.ro/ddr5-simulator | Visualizes latency from given timings; does NOT generate timings |
| DDR5 Latency Calculator | thehomeserverblog.com/ddr5-latency-calculator/ | tCK + ns calc, bandwidth, presets |
| OptimalDDR5 (GitHub) | github.com/DeSitterUniverse/OptimalDDR5 | Python: import profile, compare against OC limits |
| DDR5-OC-Guide (GitHub) | github.com/Arshia1381/DDR5-OC-Guide | Text guide: timing rules, IC characteristics |

**Gap:** nobody has built a full generator that takes inputs (speed, tCL, tRCD, tRP, density, rank) and calculates ALL derived timings automatically.

---

## JEDEC references

- **JESD79-5D (DDR5 SDRAM):** jedec.org/standards-documents/docs/jesd79-5d — main chip spec (free with registration)
- **JESD400-5D (SPD Contents):** jedec.org/standards-documents/docs/jesd400-5d01 — SPD byte map (for your SPD programmer)