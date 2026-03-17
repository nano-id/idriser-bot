# Project Blueprint

## 1) Purpose
- Target universe: top 100 liquid coins (primary quote: `USDT`).
- Engine style: market-data centric trade engine.
- Base data unit: `5m` market snapshot.
- Decision horizons: `15m`, `30m`, `1h`, `4h`, `1d`.
- Decision logic:
  - `Step2` = primary technical decision engine.
  - `Step3` = macro regime veto layer.
  - `DeepSeek` = support-only AI layer (not core decision authority).

## 2) Core Principles
- Core dependency is `Binance/CCXT` market data.
- Santiment/CryptoQuant are not core dependencies.
- Santiment/CryptoQuant can be reintroduced later only as optional modules.
- Runtime behavior must be config-driven and validation-protected.
- Gaps in market snapshots must not be treated as complete windows.

## 3) Target System Flow
1. Universe build
2. Market snapshot collection (`5m`)
3. Multi-horizon aggregation (`15m/30m/1h/4h/1d`)
4. Step2 evaluation
5. Step3 evaluation
6. Probability / trade decision
7. Reporting
8. Paper bot execution
9. Live bot execution

## 4) Current Code Status

### Implemented
- Universe building from exchange markets with fallback symbols:
  - `app/universe/builder.py`
- `5m` snapshot collection from CCXT OHLCV:
  - `app/pipeline/market_snapshot_collector.py`
- Multi-horizon aggregation with time-gap checks and runtime-configurable weights:
  - `app/pipeline/hourly_signal_aggregator.py`
  - `app/utils/timeframe.py`
- Runtime config model + JSON local store:
  - `app/models/runtime_config.py`
  - `app/config/runtime_store.py`
- Step2 technical filter + scoring:
  - `app/filters/technical_filter.py`
  - `app/scoring/step2_scorer.py`
- Step3 regime filter + scoring:
  - `app/filters/market_regime_filter.py`
  - `app/scoring/step3_scorer.py`
- Demo/runtime scripts:
  - `scripts/run_hourly_signal_demo.py`
  - `scripts/run_multi_horizon_signal_demo.py`
  - `scripts/show_runtime_config.py`

### Planned / Not Yet Implemented
- Single end-to-end orchestrator that chains:
  `universe -> snapshot -> aggregation -> Step2 -> Step3 -> final decision`
- Probability/trade-decision module (position direction, confidence, sizing-ready output).
- Report generation module for the new core flow.
- Paper bot module.
- Live bot module.
- Dashboard backend API and UI.
- DeepSeek integration layer (support-only mode).
- Hard guarantee of "top 100 liquid" ranking logic (current universe selection is configurable, but not a finalized liquidity-ranking engine).

