# OBSERVATION ONLY — NO ALERT ACTION AUTHORIZED.

# Alert Expiration Snapshot — 2026-09-26

- **Snapshot time:** 2026-09-26T10:49Z (UTC)
- **Source:** TradingView MCP `list-alerts` (read-only call). No alert was
  created, updated, stopped, restarted, deleted, or recreated.
- **48-hour window:** expirations before 2026-09-28T10:49Z are flagged.
- **Timeframe:** all alerts report resolution `15` (15m).
- **Condition type:** all alerts are `strategy` alerts, "alert() function calls only".

## Alert names (full strings as reported)

- **LAS-15** = `LAS-15 v1.0 - Liquidity Acceptance Strategy (BTCUSDT · Binance, 1, 3, 0.5, 3, 2, 0.6, 0.8, 2, 1.5, 0.5, 0.1, 12, 1.8, 0.7, 1.2, 0700-2100, BTCUSDT,ETHUSDT,SOLUSDT,HYPEUSDT,AVAXUSDT): alert() function calls only`
- **A+ v1.9 TEST** = `A+ Crypto Futures Strategy v1.9 TEST (0700-1000, 0800-1100, , BTCUSDT · Binance, 20, 200, 12, 10, 5, 6, 0.08, 14, 52, 72, 28, 48, 20, 1.25, 0.55, 14, 14, 18, 1.3, 0.25, 0.5, 50, 65, 1, 2, 14, 0.2, 10): alert() function calls only`

## Summary

| | Count |
|---|---|
| Total alerts | 22 |
| Active (all LAS-15) | 16 |
| Inactive (all A+ v1.9 TEST) | 6 |
| **Expiring within 48 h** | **12** (6 active LAS-15, 6 inactive A+ v1.9 TEST) |
| Expiring 2026-10-01 (~4 days) | 9 (all active LAS-15) |
| Expiring 2026-10-22 | 1 (active LAS-15) |

## Alerts (sorted by expiration)

| ⚠ 48h | Alert ID | Name | Symbol | TF | Active | Expiration (UTC) |
|---|---|---|---|---|---|---|
| ⚠ | 5491006269 | LAS-15 | BINANCE:ZECUSDT.P | 15m | active | 2026-09-27T18:32:54Z |
| ⚠ | 5491009251 | LAS-15 | BINANCE:SUIUSDT.P | 15m | active | 2026-09-27T18:35:32Z |
| ⚠ | 5491011465 | LAS-15 | BINANCE:ADAUSDT.P | 15m | active | 2026-09-27T18:36:14Z |
| ⚠ | 5491017455 | LAS-15 | BINANCE:BANKUSDT.P | 15m | active | 2026-09-27T18:38:53Z |
| ⚠ | 5491018510 | A+ v1.9 TEST | BINANCE:BEATUSDT.P | 15m | inactive | 2026-09-27T18:39:25Z |
| ⚠ | 5491020236 | A+ v1.9 TEST | BINANCE:SKYAIUSDT.P | 15m | inactive | 2026-09-27T18:40:36Z |
| ⚠ | 5491021645 | A+ v1.9 TEST | BINANCE:BTWUSDT.P | 15m | inactive | 2026-09-27T18:41:19Z |
| ⚠ | 5491023219 | LAS-15 | BINANCE:PYTHUSDT.P | 15m | active | 2026-09-27T18:42:30Z |
| ⚠ | 5491024963 | A+ v1.9 TEST | BINANCE:EDENUSDT.P | 15m | inactive | 2026-09-27T18:44:30Z |
| ⚠ | 5491026024 | LAS-15 | BINANCE:DOTUSDT.P | 15m | active | 2026-09-27T18:46:03Z |
| ⚠ | 5491029826 | A+ v1.9 TEST | BINANCE:NILUSDT.P | 15m | inactive | 2026-09-27T18:50:26Z |
| ⚠ | 5491030647 | A+ v1.9 TEST | BINANCE:GIGGLEUSDT.P | 15m | inactive | 2026-09-27T18:51:08Z |
| | 5494027470 | LAS-15 | BINANCE:BTCUSDT.P | 15m | active | 2026-10-01T12:22:12Z |
| | 5500360747 | LAS-15 | BINANCE:UNIUSDT.P | 15m | active | 2026-10-01T12:29:05Z |
| | 5500378040 | LAS-15 | BINANCE:SOLUSDT.P | 15m | active | 2026-10-01T12:30:34Z |
| | 5500390059 | LAS-15 | BINANCE:HYPEUSDT.P | 15m | active | 2026-10-01T12:31:40Z |
| | 5500402546 | LAS-15 | BINANCE:TAOUSDT.P | 15m | active | 2026-10-01T12:32:45Z |
| | 5500413205 | LAS-15 | BINANCE:LDOUSDT.P | 15m | active | 2026-10-01T12:33:35Z |
| | 5500426255 | LAS-15 | BINANCE:JUPUSDT.P | 15m | active | 2026-10-01T12:34:45Z |
| | 5500441363 | LAS-15 | BINANCE:SEIUSDT.P | 15m | active | 2026-10-01T12:35:27Z |
| | 5500487583 | LAS-15 | BINANCE:KERNELUSDT.P | 15m | active | 2026-10-01T12:36:11Z |
| | 5491028912 | LAS-15 | BINANCE:TUTUSDT.P | 15m | active | 2026-10-22T19:12:05Z |

## Observations

1. Six **active** LAS-15 alerts (ZEC, SUI, ADA, BANK, PYTH, DOT) expire
   2026-09-27 between 18:32Z and 18:47Z. After expiry, those symbols would no
   longer produce LAS-15 alerts.
2. The remaining nine 2026-10-01 LAS-15 alerts, including BTCUSDT.P, expire
   roughly four days after this snapshot.
3. The six A+ v1.9 TEST alerts expiring 2026-09-27 are already inactive.
4. Correction to the earlier environment audit: that audit said 17 active
   alerts and 9 expiring tomorrow (including TUT). The verified figures are
   16 active; 12 expiring within 48 h (6 of them active); and TUT expires
   2026-10-22.

Any renewal or other alert action is for the user to decide and perform, and
is outside this repository's authority (`CONTROL/CHANGE_CONTROL.md`).
