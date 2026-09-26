# EVENT IDENTITY — RESEARCH SPECIFICATION v0.1

> **RESEARCH SPECIFICATION ONLY.** This document does not describe, modify,
> or authorise changes to production LAS-15 Pine.

## 1. Purpose

The event-identity defect is confirmed at the reporting layer
(`CONTROL/RESEARCH_STATUS.md`). Downstream stages (WATCH, CT/displacement,
FVG, entry) cannot currently be attributed with certainty to the liquidity
event that started the lineage. This spec defines how identity is to be
recorded in research so that attribution claims are only made when backed by
identity evidence.

## 2. Two independent identifiers

### RESEARCH_CASE_ID

- Assigned by the **research process**, one per research case.
- Always present; unique within the research dataset.
- Carries no claim about production behaviour.
- Exists for both legacy and prospective cases.

### LIVE_EVENT_SEQ

- An identifier that **production** would emit for a liquidity event and carry
  through every downstream stage of that event's lineage.
- **LIVE_EVENT_SEQ does NOT currently exist in verified production Pine.**
- It is a **proposed measurement mechanism** only. Its implementation in Pine
  is not authorised by this spec.
- May be `null`. Must be `null` unless it was actually emitted by verified
  production event identity. It is **never** inferred, reconstructed,
  back-filled, or invented by research code.

The two identifiers are independent: a RESEARCH_CASE_ID never implies a
LIVE_EVENT_SEQ, and the absence of LIVE_EVENT_SEQ never invalidates a
research case.

## 3. Intended lineage

```
LIQUIDITY EVENT
  → RESOLUTION
  → WATCH
  → CT / DISPLACEMENT
  → FVG
  → PULLBACK
  → ENTRY
  → TERMINAL STATE
```

Each stage, when production event identity exists, would carry the
LIVE_EVENT_SEQ of the originating liquidity event. A downstream stage is
attributed to the originating event with certainty only when its own recorded
event sequence equals the case's LIVE_EVENT_SEQ.

## 4. Attribution rules (enforced by the research data model)

| Attribution | Allowed values | Certain value | Requirement for the certain value |
|---|---|---|---|
| WATCH | `EXACT`, `NO_WATCH_FOR_ORIGINAL_EVENT`, `AMBIGUOUS_EVENT_IDENTITY`, `INSUFFICIENT_DATA`, `UNATTRIBUTED` | `EXACT` | `LIVE_EVENT_SEQ` non-null **and** `WATCH_EVENT_SEQ == LIVE_EVENT_SEQ` |
| FVG | `SAME_EVENT`, `AMBIGUOUS_EVENT_IDENTITY`, `INSUFFICIENT_DATA`, `UNATTRIBUTED` | `SAME_EVENT` | `LIVE_EVENT_SEQ` non-null **and** `FVG_EVENT_SEQ == LIVE_EVENT_SEQ` |

Default attribution is `UNATTRIBUTED`. Because legacy cases can never hold a
LIVE_EVENT_SEQ, they can never be classified `EXACT` / `SAME_EVENT`.

## 5. Known historical classifications

| Case | Classification |
|---|---|
| P4_ORIGINAL_EVENT_WATCH | NO_WATCH_FOR_ORIGINAL_EVENT |
| P5_ORIGINAL_EVENT_WATCH | NO_WATCH_FOR_ORIGINAL_EVENT |
| P6_ORIGINAL_EVENT_WATCH | AMBIGUOUS_EVENT_IDENTITY |
| P7_M2_NONREGISTRATION | INSUFFICIENT_DATA |

All historical cases remain **`PRE_EVENTSEQ_LEGACY`**. No eventSeq values are
assigned to them, now or retroactively.

## 6. Out of scope

- Implementing eventSeq in Pine.
- Any change to production logic, alerts, or watchlist.
- Any claim that research lineage matches production lineage.

See `PROSPECTIVE_EVENT_SCHEMA_v0.1.md` for the record schema and
`research_model.py` for the enforcing data model.
