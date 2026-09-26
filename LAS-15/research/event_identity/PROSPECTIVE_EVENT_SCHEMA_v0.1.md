# PROSPECTIVE EVENT SCHEMA v0.1

> **RESEARCH-ONLY SCHEMA.** For future research records. Not a production
> data format. Prospective enrollment is **NOT AUTHORIZED**; this schema only
> defines the record shape. Enforced by `research_model.py` (`EventRecord`).

Timestamps are ISO-8601 UTC strings. `null` means "not observed / not
applicable / not available" — never a guess.

## Core fields (requested)

| Field | Type | Nullable | Notes |
|---|---|---|---|
| SYMBOL | string | no | `EXCHANGE:TICKER`, e.g. `BINANCE:BTCUSDT.P` |
| RESEARCH_CASE_ID | string | no | Assigned by research; see identity spec |
| LIVE_EVENT_SEQ | integer | **yes** | `null` until production event identity exists. **Never fabricated.** Must be `null` for `PRE_EVENTSEQ_LEGACY` |
| EVENT_DIRECTION | `BUY_SIDE` \| `SELL_SIDE` | yes | Side of liquidity taken |
| TESTED_LEVEL | number | yes | Liquidity level tested |
| SWEEP_EXTREME | number | yes | Extreme price of the sweep |
| EVENT_TIMESTAMP | timestamp | yes | |
| RESOLUTION_TIMESTAMP | timestamp | yes | |
| THESIS_CLOSE_TIMESTAMP | timestamp | yes | |
| THESIS_CLOSE_REASON | string | yes | |
| WATCH_TIMESTAMP | timestamp | yes | |
| CT_TIMESTAMP | timestamp | yes | CT / displacement |
| FVG_TIMESTAMP | timestamp | yes | |
| PULLBACK_TIMESTAMP | timestamp | yes | |
| ENTRY_TIMESTAMP | timestamp | yes | |
| BTC_CONTEXT | string | yes | |
| ASSET_4H_CONTEXT | string | yes | |
| ASSET_1H_CONTEXT | string | yes | |
| M2_CLASS | string | yes | |
| EVENT_FAMILY | string | yes | |
| FTA | number | yes | |
| STRUCTURAL_STOP | number | yes | |
| R_TO_FTA | number | yes | |
| DATA_PROVENANCE | string | no | Where/how the record was obtained; required, non-empty |

## Supporting fields (added for identity enforcement)

These are not part of the requested core list; they exist so the model can
enforce the attribution rules in `EVENT_IDENTITY_SPEC_v0.1.md`.

| Field | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| CASE_ERA | `PRE_EVENTSEQ_LEGACY` \| `PROSPECTIVE` | no | — | Legacy cases cannot carry any eventSeq |
| WATCH_EVENT_SEQ | integer | yes | `null` | eventSeq carried by the WATCH stage |
| FVG_EVENT_SEQ | integer | yes | `null` | eventSeq carried by the FVG stage |
| WATCH_ATTRIBUTION | enum | no | `UNATTRIBUTED` | `EXACT` requires identity evidence |
| FVG_ATTRIBUTION | enum | no | `UNATTRIBUTED` | `SAME_EVENT` requires identity evidence |

## Governance defaults (`ResearchGovernance`)

| Field | Default |
|---|---|
| PRODUCTION_CHANGE_JUSTIFIED | `NO` |
| PROSPECTIVE_ENROLLMENT | `NOT_AUTHORIZED` |
