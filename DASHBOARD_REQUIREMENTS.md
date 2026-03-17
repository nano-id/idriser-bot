# Dashboard Requirements

## Scope
- Dashboard is a control panel, not only a monitoring screen.
- Primary goal: safe runtime control of analysis and bot lifecycle.
- UI decisions must respect backend validation and audit constraints.

## Sections

### 1) Overview
- Global status summary:
  - exchange connectivity
  - universe size and symbol coverage
  - latest snapshot/aggregation timestamps
  - Step2/Step3 pass rates
  - active bot mode (`disabled/paper/live`)

### 2) Signal Monitor
- Multi-horizon signal board (`15m/30m/1h/4h/1d`).
- Per-symbol aggregate metrics:
  `mean_signal`, `bullish_ratio`, `stability_score`, window completeness.
- Fast filters:
  horizon, score range, Step2 pass, Step3 pass, fallback/time-gap flags.

### 3) Coin Detail
- Single-symbol deep view:
  - latest `5m` snapshots
  - aggregate history by horizon
  - Step2 technical breakdown
  - Step3 regime/veto reasoning

### 4) Runtime Config
- Must allow runtime override for:
  - universe
  - snapshot
  - decision horizon
  - aggregation weights
  - Step2 thresholds
  - Step3 thresholds
  - DeepSeek settings
  - risk settings
  - paper/live mode
- Every setting change must:
  - support runtime override
  - pass validation before apply
  - create audit/log event with timestamp + actor + old/new values

### 5) Strategy Profiles
- Named profile sets (e.g. conservative/aggressive).
- Profile switch should update runtime config atomically.
- Invalid profile payload must be rejected with explicit validation errors.

### 6) Bot Control
- Actions:
  - start
  - stop
  - mode switch (`disabled/paper/live`)
  - profile select
  - emergency stop
- Must show action result and current bot state after each command.

### 7) Logs / Events
- Unified event stream:
  - config changes
  - mode changes
  - signal pipeline warnings (fallbacks, data gaps)
  - risk triggers
  - order lifecycle (paper/live when implemented)

## API Needs (List Only)
- Health/status endpoints.
- Universe read endpoints.
- Snapshot read endpoints.
- Multi-horizon aggregate read endpoints.
- Step2/Step3 result read endpoints.
- Runtime config read/update/reset endpoints.
- Strategy profile CRUD/select endpoints.
- Bot control command endpoints (start/stop/mode/profile/manual close/emergency stop).
- Bot state/position/order read endpoints.
- Logs/events query and stream endpoints.
- Audit log query endpoints.

## Current Implementation Alignment
- Implemented foundation:
  - runtime config model/store (`RuntimeConfig`, `RuntimeConfigStore`)
  - snapshot + aggregation + Step2/Step3 core components
- Not yet implemented:
  - dashboard UI
  - dashboard backend API layer
  - profile manager
  - bot control endpoints
  - full audit/event service

