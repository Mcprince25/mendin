# CHANGE CONTROL

## Frozen status

| Component | Status |
|---|---|
| LAS-15 A+ | **FROZEN CONTROL** |
| A-Early | **EXPERIMENTAL** |
| Production Pine | **NOT PRESENT IN CLOUD REPOSITORY YET** |

**No modification without GPT/user approval.**

Approval must be explicit and specific to the change. Tool availability
(including write-capable TradingView MCP tools in a session) is **never**
authorisation.

## Prohibited automatic changes

None of the following may be changed automatically, or as a side effect of
research work, in production or in any artefact claiming to represent
production:

- M1
- M2
- liquidity definitions
- resolution
- WATCH
- CT / displacement
- FVG
- entry
- stop
- FTA
- R threshold
- BTC gate
- risk
- alerts
- watchlist

## Rules

1. Research findings do not by themselves justify a production change
   (see `RESEARCH_STATUS.md`: `PRODUCTION_CHANGE_JUSTIFIED = NO`).
2. Research code is not production code and must not be presented as
   equivalent to production Pine (see `SOURCE_OF_TRUTH.md`).
3. Every approved change must record: what changed, who approved it, the
   evidence cited, and the validation performed against the authoritative
   source.

## Change log

| Date | Change | Approved by | Evidence | Validation |
|---|---|---|---|---|
| 2026-09-26 | Research repository foundation created (documentation, schema, research data model, tests). No production change. | GPT/user (foundation-build task) | n/a | n/a |
| 2026-09-26 | Added research-only module `research/early_rebreak/` (EARLY_REBREAK_RESEARCH_v0.1: protocol, status, data model, tests). No change to A+, A-Early, production Pine, alerts or any frozen definition. Enrollment not authorized. | GPT/user (rebreak research-design task) | n/a | n/a (research model tests only) |
