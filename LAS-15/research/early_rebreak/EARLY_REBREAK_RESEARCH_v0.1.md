# EARLY_REBREAK_RESEARCH_v0.1 — CRT / Rebreak Early-Entry Experiment

| Item | Value |
|---|---|
| STATUS | **EXPERIMENTAL** |
| PRODUCTION_AUTHORIZED | **NO** |
| PINE_IMPLEMENTATION_AUTHORIZED | **NO** |
| LIVE_ALERT_IMPLEMENTATION_AUTHORIZED | **NO** |
| PROSPECTIVE_ENROLLMENT | **NOT_AUTHORIZED** |
| PROTOCOL_COMPLETE | **NO** |
| MISSING_AUTHORITATIVE_DEFINITIONS | **YES** — see §15 |
| PROTOCOL_READY_FOR_ENROLLMENT | **NO** (enforced by `ProtocolDependencies` gate in the model) |
| LAS-15 A+ | FROZEN CONTROL (unchanged; Branch C only) |
| A-Early | EXPERIMENTAL (unchanged; not part of this module) |

Research design and offline data model only. Nothing here changes LAS-15
A+, A-Early, production Pine, alerts or watchlists. Data model:
[`rebreak_model.py`](rebreak_model.py). Tests: `../../tests/test_rebreak_model.py`.

---

## 1. Research question

LAS-15 has one weakness under study here: **late entry.**

> After a VALID LAS-15 meaningful HTF location + liquidity event + confirmed
> acceptance/rejection, can an objective control break followed by a
> lower-timeframe pullback and REBREAK provide a materially earlier and more
> precise A-entry than waiting for the full LAS-15 A+ FVG/retest, WITHOUT
> materially increasing false entries or damaging expectancy?

## 2. Source concept, and what was extracted from it

The source is an external CRT methodology reviewed by GPT. **CRT is not being
imported as a strategy.**

| Source element | Treatment |
|---|---|
| C1 range / C2 sweep and close back inside / C3 break of the opposite side of C2 | **Not copied.** C2 high/low is replaced by the LAS-15 `CT_REFERENCE` (§6) |
| Direct break execution | Tested as Branch A |
| Rebreak execution (first break → LTF pullback → rebreak) | Tested as Branch B |
| Claimed 60 / 70 / 80 / 85 % win rates | **UNVERIFIED_EXTERNAL_CLAIM.** Not evidence for LAS-15 |

**Rejected, not imported:**

- a fixed stop placement derived from 1.5R;
- any stop placement designed to manufacture R:R;
- a mandatory session restriction;
- the first-setup-of-session rule;
- CRT as a replacement for LAS-15;
- the claimed win rates;
- prop-firm-specific risk rules.

Extracted mechanism only:

```
VALID LOCATION → LIQUIDITY EVENT → REJECTION / ACCEPTANCE
  → CONTROL BREAK → LOWER-TIMEFRAME PULLBACK → REBREAK → EARLY A-ENTRY
```

## 3. Frozen control (unchanged)

```
BTC CONTEXT → ASSET 4H/1H CONTEXT → MEANINGFUL LOCATION → LIQUIDITY EVENT
  → ACCEPTANCE/REJECTION → DISPLACEMENT / STRUCTURAL SHIFT → POST-MSS FVG
  → RETRACEMENT → ENTRY → STRUCTURAL INVALIDATION → FTA
```

The A+ signal is **observed and recorded** exactly as the frozen A+ produces
it. This module does not define, re-implement or approximate A+ logic.

## 4. Three branches, one parent event

| Branch | Sequence after the valid parent thesis | Trigger stage |
|---|---|---|
| A — `DIRECT_CONTROL_BREAK` | first confirmed 15m close through CT_REFERENCE → hypothetical early signal | `control_break` |
| B — `PULLBACK_REBREAK` | CT break → controlled 1m/3m pullback → confirmed rebreak → hypothetical early signal | `rebreak` |
| C — `FROZEN_A_PLUS` | frozen A+: displacement → post-MSS FVG → retracement → A+ signal | `a_plus_signal` |

All three branches live in one `EarlyRebreakCase` with one `ParentEvent`. They
therefore always share the same parent identity. A branch signal cannot
precede its trigger stage, and a branch's direction must match the parent
thesis.

## 5. Event identity (mandatory)

This section builds on `../event_identity/EVENT_IDENTITY_SPEC_v0.1.md`.

- **Parent:** `RESEARCH_CASE_ID` (always present) and `LIVE_EVENT_SEQ`
  (null until production event identity exists; **never fabricated**).
- **Downstream sequence fields:** `WATCH_EVENT_SEQ`,
  `CONTROL_BREAK_EVENT_SEQ`, `PULLBACK_EVENT_SEQ`, `REBREAK_EVENT_SEQ`,
  `FVG_EVENT_SEQ`, `A_PLUS_EVENT_SEQ`. In the model, each is the
  `event_seq` field of its stage object.
- **Attribution is computed, never declared.**
  - `SAME_EVENT` requires that the parent `LIVE_EVENT_SEQ` is non-null and
    the stage eventSeq equals it.
  - Every other case gives **`AMBIGUOUS`**. Temporal proximity alone never
    gives SAME_EVENT.
- **Rejected with `IdentityError`:**
  - a stage whose eventSeq differs from the parent's (for example, a later
    parent inheriting an older event's WATCH, CT, FVG or rebreak);
  - a stage carrying an eventSeq when the parent has none;
  - a stage timestamped before the parent event;
  - any eventSeq on a `PRE_EVENTSEQ_LEGACY` case.

Motivation: the N=10 diagnostic exposed possible WATCH/FVG misattribution
between old and new liquidity events (`EVENT_IDENTITY_DEFECT = CONFIRMED AT
REPORTING LAYER`).

## 6. Eligible parent event

A parent becomes eligible only when all five conditions hold. Otherwise
`eligibility_failures()` names the reason:

| # | Condition | Failure code |
|---|---|---|
| 1 | BTC not `BTC_HARD_VETO` | `BTC_HARD_VETO` |
| 2 | Asset 4H and 1H context captured | `ASSET_4H_1H_CONTEXT_NOT_CAPTURED` |
| 3 | M2 location `VALID` | `M2_LOCATION_NOT_VALID` |
| 4 | Objective liquidity event (`EVENT_TIMESTAMP`, `TESTED_STRUCTURAL_LEVEL`, `SWEEP_EXTREME` required) | enforced at construction |
| 5 | Initial acceptance/rejection confirmed (`INITIAL_RESOLUTION_TIMESTAMP`) | `ACCEPTANCE_REJECTION_NOT_CONFIRMED` |

- Ineligible parents are **recorded, not discarded**. They cannot carry a CT
  reference, stages or branches.
- **Parent fields recorded:**
  - location: `M2_TYPE`, `M2_TIMEFRAME`, `EXTERNAL_OR_INTERNAL`,
    `TESTED_STRUCTURAL_LEVEL`, `SWEEP_EXTREME`, `FIRST_RETEST`,
    `PRIOR_REACTION_COUNT`, `ACTIVE_RANGE_POSITION`;
  - direction: `EVENT_DIRECTION` (BUY_SIDE/SELL_SIDE),
    `THESIS_DIRECTION` (LONG/SHORT), `EVENT_KIND` (REVERSAL/CONTINUATION);
  - context: `HTF_ALIGNMENT`, `BTC_STATE`, `LOCATION_CLASS`,
    `LOCATION_CLASSIFIED_AT`, `PA_REGIME`, `PROTOCOL_VERSION`.
- `TESTED_STRUCTURAL_LEVEL` and `SWEEP_EXTREME` are separate, independently
  required fields. Sanity check: for a SELL_SIDE event, the sweep extreme is
  at or below the level; for BUY_SIDE, at or above.
- For a REVERSAL, SELL_SIDE liquidity implies a LONG thesis and BUY_SIDE
  implies SHORT.

## 7. Control-transfer reference (CT_REFERENCE)

- **Definition:** CT_REFERENCE is the most recently confirmed opposing 15m
  structural pivot within `EVENT_START → INITIAL_RESOLUTION`. It is frozen
  at INITIAL_RESOLUTION.
  - A LONG thesis needs an opposing pivot HIGH; a SHORT thesis needs a
    pivot LOW.
  - The model enforces the window, confirmation by resolution, and the
    opposing pivot type.
- **Pivot definition:** `RC1_PENDING_IMPORT_FROM_FROZEN_RESEARCH`. The
  frozen RC1 pivot definition is **not present in this repository**. It must
  be imported exactly before enrollment.
  - Note: `PIVOT_FIDELITY_DEFECT = MATERIAL_RESEARCH_FIDELITY_DEFECT` in
    `CONTROL/RESEARCH_STATUS.md` applies directly to CT_REFERENCE.
    Resolving it is a precondition for trustworthy CT measurements.
- **DIRECT_CONTROL_BREAK:** the first confirmed 15m **close** through
  CT_REFERENCE in the thesis direction, after INITIAL_RESOLUTION. An
  intrabar wick is not confirmation (`confirmed_by` must be `CLOSE_15M`).
  - "First" is a recording obligation. The model cannot verify it without
    bar data.
- **Raw fields, with no thresholds:**
  - `CT_REFERENCE_PRICE`, `CT_REFERENCE_TIMESTAMP`,
    `CT_CONFIRMATION_TIMESTAMP`;
  - `CT_BREAK_TIMESTAMP`, `CT_BREAK_BODY_ATR`, `CT_BREAK_RANGE_ATR`,
    `CT_CLOSE_LOCATION`.

## 8. Lower-timeframe pullback and rebreak

- 1m or 3m only, for **execution precision only**. The 15m thesis must
  already exist. The LTF never creates the thesis.
- Required order: `15m CT break → LTF pullback → LTF rebreak`.
  - A rebreak requires both a control break and a pullback.
  - A rebreak must come strictly after the CT break, and at or after the
    pullback end (or start, if the end is unrecorded).
- **`PULLBACK_DEFINITION = PENDING_RESEARCH`.** No frozen pullback
  definition exists in the repository. The 24H pullback protocol's
  definition is itself `PENDING_IMPORT_FROM_FROZEN_RESEARCH`, and it is a
  different, pre-event concept. **No threshold is invented.**
- Candidate raw measurements (none is a filter):
  - depth %
  - depth ATR
  - bars in pullback
  - close back through CT (Y/N)
  - adverse excursion
  - wick/body notes
  - VWAP relation
  - local micro swing

## 9. Structural invalidation

```
thesis invalidation → structural stop → risk → position size
```

Never `desired R → stop`.

- **`StopSource` values:**
  - `ORIGINAL_LIQUIDITY_EXCURSION`
  - `THESIS_INVALIDATING_EXTREME`
  - `ACCEPTED_STRUCTURAL_BOUNDARY`
  - `FROZEN_A_PLUS_RULE` (A+ branch only)

  R-derived sources (`DESIRED_R`, `FIXED_R`, `R_MULTIPLE`, `TARGET_RR`,
  `FIXED_1_5R`) are rejected.
- **Allowed thesis-stop sources:**
  - REVERSAL: `ORIGINAL_LIQUIDITY_EXCURSION` or
    `THESIS_INVALIDATING_EXTREME`. An excursion-based stop must sit at or
    beyond `SWEEP_EXTREME`.
  - CONTINUATION: `ACCEPTED_STRUCTURAL_BOUNDARY` or
    `THESIS_INVALIDATING_EXTREME`.
- **Branches A and B must use the parent's thesis stop exactly.** An early
  entry does not justify a tighter stop.
- **Branch C records the stop that the frozen A+ produces.**
- The exact LAS-15 reversal and continuation invalidation rules are not in
  the repository. They must be imported before enrollment.
- **Direction sanity:** LONG requires `STOP < ENTRY < FTA`; SHORT requires
  `STOP > ENTRY > FTA`.
  - Anything else is `INVALID_GEOMETRY`: no R is computed and the trade
    cannot be marked eligible.
  - If the stop or FTA is missing, the geometry is `INCOMPLETE`.
- **Recorded:** `STRUCTURAL_STOP`, `STOP_SOURCE`, `STOP_DISTANCE`,
  `STOP_DISTANCE_ATR` (using `atr_15m`).

## 10. FTA and R

- FTA hierarchy: meaningful 4H obstacle → meaningful 1H obstacle →
  meaningful external 15m obstacle (`FTA_4H`, `FTA_1H`, `FTA_15M_EXTERNAL`).
  The full selection rules are to be imported from frozen research.
- An `FtaSelection` is immutable and timestamped. `selected_at` must be at or
  before the branch entry.
- R is computed only by `compute_r_to_fta(direction, entry, StructuralStop,
  FtaSelection)`. A raw number is not accepted as the FTA.
- Per branch: `DIRECT_BREAK_R_TO_FTA`, `REBREAK_R_TO_FTA`, `A_PLUS_R_TO_FTA`,
  each from that branch's own entry against the frozen stop and FTA.
- The FTA and stop are never moved to manufacture acceptable R.

## 11. Primary comparison (per parent event)

| Measure | Model |
|---|---|
| EVENT → RESOLUTION, RESOLUTION → CT break, CT break → rebreak, CT break → A+, REBREAK → A+ | `case.latencies` |
| PRICE_AT_CT_BREAK, PRICE_AT_REBREAK, PRICE_AT_A_PLUS | `case.prices` |
| MOVE_CONSUMED_BEFORE_DIRECT_ENTRY / _REBREAK / _A_PLUS | `case.move_consumed_before_entry` |
| ENTRY_DISTANCE_FROM_STRUCTURAL_STOP | `branch.stop_distance` |
| R_TO_FTA | `branch.r_to_fta` |

`MOVE_CONSUMED` (v0.1) is the signed thesis-direction distance from
`SWEEP_EXTREME` to the branch entry price. **Does REBREAK solve late entry?**
Answering needs, for the same parents, smaller move consumed and shorter
latency than A+, without worse false-break frequency or expectancy.

## 12. Outcomes

- **Per branch:**
  - signal: `SIGNAL_YES_NO`, `TRADE_ELIGIBLE_YES_NO`
  - trade geometry: `ENTRY_PRICE`, `STRUCTURAL_STOP`, `FTA`, `R_TO_FTA`
  - first touch: `FTA_FIRST` / `STOP_FIRST` / `NEITHER` /
    `RIGHT_CENSORED`
  - excursions: `MFE`, `MAE` (as price distances), `MFE_R`, `MAE_R`
  - `REALIZED_R`: gross; `FTA_FIRST` = R_TO_FTA, `STOP_FIRST` = −1,
    otherwise null
- **Later aggregates (not computed now):**
  - signal frequency and trade eligibility
  - win rate, average win R, average loss R
  - expectancy, profit factor, drawdown
  - false-break frequency and missed-good-move frequency
  - entry latency and move consumed
- **A 50 %+ win rate is a DEVELOPMENT OBJECTIVE, not evidence.** No target
  is reported as achieved.

## 13. Stratification (never pooled blindly)

`ParentEvent.stratum = (HTF_ALIGNMENT, BTC_STATE, LOCATION_CLASS, PA_REGIME)`

- **HTF alignment:** `WITH_HTF`, `COUNTER_HTF`, `RANGE`, `TRANSITION`.
  The N=10 diagnostic was dominated by COUNTER_HTF.
- **BTC state:** `BTC_TREND`, `BTC_NEUTRAL`, `BTC_STRESS`, `BTC_HARD_VETO`.
  HARD_VETO parents are ineligible.
- **Location class**, fixed at `LOCATION_CLASSIFIED_AT`, which must precede
  any entry and outcome:
  - `MAJOR_EXTERNAL_4H`, `MAJOR_EXTERNAL_1H`
  - `ACTIVE_RANGE_BOUNDARY`, `BROKEN_HTF_LEVEL_FIRST_RETEST`
  - `INTERNAL_1H`, `INTERNAL_15M`, `OTHER_VALID_M2`

  Records are immutable, so no reclassification is possible after the
  outcome is known.
- **PA regime (research labels only, not a filter):** `CLEAN_DIRECTIONAL`,
  `WICKY_DIRECTIONAL`, `TWO_SIDED_VOLATILITY`, `CHOP`, `TRANSITION`,
  `UNKNOWN`.

Hypotheses to test, not adopted:

- A clean directional regime may favour DIRECT BREAK.
- A wicky or aggressive regime may benefit from REBREAK.
- Chop may make both unreliable.

Failure attribution to investigate:

- `EVENT_QUALITY`
- `HTF_ALIGNMENT`
- `ENTRY_TIMING`
- `EVENT_IDENTITY`
- any combination of these.

Integration with the major vs. minor sweep research: do upward moves after
sell-side sweeps differ by the swept level's class and timeframe?

## 14. Sample standard and discipline

- Checkpoints: **N=10 → N=25 → N=50 → N=75 → N=100** (development
  conclusion). Each advance requires GPT/user authorisation.
- **Enrollment is NOT started and NOT authorised.**
- No threshold fitting to early winners, and no discarding of losing cases.
- Any definition change after outcomes are seen requires a new
  `PROTOCOL_VERSION` and a restart or segregation of the affected sample.

## 15. Preconditions before any enrollment request

Blocking dependencies (model: `ProtocolDependencies`; all currently NOT met).
`PROTOCOL_READY_FOR_ENROLLMENT` is YES only when every one is met, and even
then enrollment still requires explicit GPT/user authorisation. None of these
may be invented to make the experiment executable. The pivot algorithm is not
modified here; `PIVOT_FIDELITY_DEFECT = MATERIAL_RESEARCH_FIDELITY_DEFECT`
is preserved pending the authoritative-source import.

| Dependency | Status |
|---|---|
| CT_REFERENCE_DEFINITION_IMPORTED (RC1) | NO |
| STRUCTURAL_STOP_RULES_IMPORTED | NO |
| FTA_RULES_IMPORTED | NO |
| PULLBACK_DEFINITION_RESOLVED | NO |
| PIVOT_FIDELITY_STATUS_RESOLVED_FOR_EXPERIMENT | NO |
| OUTCOME_HORIZON_RESOLVED | NO |
| SAME_BAR_STOP_FTA_POLICY_RESOLVED | NO |

Checklist:

1. Import the frozen RC1 pivot definition, and address the pivot-fidelity
   defect.
2. Import the frozen LAS-15 structural-invalidation rules for reversal and
   continuation events.
3. Import the frozen FTA selection rules.
4. Define and pre-register the pullback definition, or keep Branch B as
   raw-measurement only.
5. Fix the outcome observation horizon (the right-censoring rule).
6. Define the "first-touch" resolution when the stop and FTA are hit in
   the same bar.
7. Establish the data source and provenance for 15m and 1m/3m bars.
8. Obtain GPT/user authorisation for N=10.
