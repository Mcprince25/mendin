# LAS-15

**PROJECT:** LAS-15 crypto-futures research and validation.

**PRIMARY EXECUTION TIMEFRAME:** 15m.

This repository is a **research** repository. It does not contain, and is not
authorised to modify, the live production LAS-15 strategy. See
[`CONTROL/CHANGE_CONTROL.md`](CONTROL/CHANGE_CONTROL.md) and
[`CONTROL/SOURCE_OF_TRUTH.md`](CONTROL/SOURCE_OF_TRUTH.md).

## Architecture

```
BTC CONTEXT
  → ASSET 4H/1H CONTEXT
  → MEANINGFUL LOCATION
  → LIQUIDITY EVENT
  → RESOLUTION
  → DISPLACEMENT / CONTROL TRANSFER
  → EXECUTION
  → STRUCTURAL INVALIDATION
  → FTA
  → RISK
```

## Research principles

- A **liquidity sweep alone is NOT an entry.**
- **No production modification is permitted merely because a research
  correlation appears promising.**
- **100 independent eligible cases** are required before a final development
  conclusion.
- Interim checkpoints: **N=10 → N=25 → N=50 → N=75 → N=100.**
  An interim checkpoint is a review point, not a conclusion. Advancing past
  any checkpoint requires GPT/user authorisation.

## Layout

| Path | Purpose |
|---|---|
| `CONTROL/` | Change control, source-of-truth record, current research status |
| `production/` | Placeholder for the authoritative production Pine (not yet imported) |
| `research/event_identity/` | Event-identity research spec, prospective schema, research data model |
| `research/liquidity_sweeps/` | Liquidity-sweep research |
| `research/pullback_hypothesis/` | 24H pullback × sell-side sweep hypothesis (draft protocol only) |
| `research/a_early/` | A-Early (experimental) research |
| `research/early_rebreak/` | CRT/rebreak early-entry experiment (EXPERIMENTAL, research only, enrollment not authorized) |
| `research/observations/` | Free-form observations |
| `data/` | Research data (`raw/`, `processed/`) — no fabricated data |
| `tests/` | Tests for the **research data model only** (not Pine regression tests) |
| `reports/` | Observation reports |
| `docs/` | Supporting documentation |

## Running tests

```
cd LAS-15
pytest
```
