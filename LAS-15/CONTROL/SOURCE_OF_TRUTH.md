# SOURCE OF TRUTH

Recorded 2026-09-26 from the cloud-session capability audit.

| Item | Status |
|---|---|
| CLOUD_TRADINGVIEW_MCP | AVAILABLE |
| CLOUD_MARKET_DATA | AVAILABLE |
| CLOUD_ALERT_READ | AVAILABLE |
| CLOUD_ALERT_WRITE_TOOLS | AVAILABLE_BUT_NOT_AUTHORIZED |
| CLOUD_LIVE_PINE | UNAVAILABLE |
| CLOUD_STRATEGY_TESTER | UNAVAILABLE |
| CLOUD_CHART_CONTROL | UNAVAILABLE |
| AUTHORITATIVE_PRODUCTION_PINE | NOT_YET_IMPORTED |
| AUTHORITATIVE_PRODUCTION_VALIDATION | REQUIRES_LOCAL_TRADINGVIEW_ENVIRONMENT |

## Binding statement

**Repository research code must NEVER be assumed equivalent to production
Pine unless verified against the authoritative live source.**

Consequences:

- The production LAS-15 Pine source must not be reconstructed from memory.
- No replacement production Pine script may be created in this repository.
- No claim of production parity or Strategy Tester regression equivalence may
  be made from this repository.
- The authoritative Pine source must be supplied from the verified local
  TradingView environment. When imported, record here the import date, the
  source, and how its identity with the live script was verified.
