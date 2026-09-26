# data/

- `raw/` — unmodified source data exactly as obtained.
- `processed/` — data derived from `raw/` by scripted, reproducible steps.

## Rules

- **No fabricated data.** Every record must carry `DATA_PROVENANCE` describing
  where it came from and how.
- `LIVE_EVENT_SEQ` must remain `null` unless it was emitted by verified
  production event identity. It is never inferred, back-filled, or invented.
- Historical cases are `PRE_EVENTSEQ_LEGACY` and never receive eventSeq values.
- No credentials, API keys, or account exports containing secrets.

Currently empty: no datasets have been imported.
