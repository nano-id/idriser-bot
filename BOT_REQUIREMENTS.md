# Bot Requirements

## 1) Architecture Boundary
- Analysis engine and execution bot must be separate modules.
- Analysis engine produces decision-ready signals; execution bot consumes them.
- Execution logic must not bypass risk rules or config validation.

## 2) Delivery Order
1. `paper bot` (first mandatory phase)
2. `live bot` (after paper stability criteria)

## 3) Bot Subcomponents
- `signal consumer`
  - reads latest approved outputs from analysis pipeline
  - rejects stale/incomplete/fallback-critical signals based on policy
- `order manager`
  - creates/cancels/modifies orders
  - tracks order states until terminal status
- `position manager`
  - tracks open/closed positions, average entry, realized/unrealized PnL
- `stop manager`
  - applies stop-loss / take-profit / trailing logic
- `risk manager`
  - enforces global and per-trade risk constraints before each action
- `execution logger`
  - writes immutable event records for decisions and exchange actions

## 4) Risk Rules (Minimum Set)
- `max open positions`
- `per-trade risk`
- `cooldown`
- `daily loss limit`
- `correlated exposure limit`

## 5) Modes
- `disabled`
  - no order generation, no position changes
- `paper`
  - simulated execution only, full logging enabled
- `live`
  - real execution on exchange credentials, strict risk gates enabled

## 6) Dashboard Interaction Contract
- `start/stop`
- `mode switch`
- `profile select`
- `manual close`
- `emergency stop`

## 7) Safety and Audit Expectations
- Every control action must be authenticated and logged.
- Mode changes must be explicit and two-step confirmable for `live`.
- Emergency stop must be immediate and idempotent.
- Runtime config changes affecting risk must be validated before apply.

## 8) Current Repo Status

### Implemented
- Analysis-side building blocks exist:
  - `5m` snapshot collection
  - multi-horizon aggregation
  - Step2 technical filter
  - Step3 regime veto filter
  - runtime config store foundation

### Planned / Not Yet Implemented
- Dedicated signal-to-trade decision service for bot consumption.
- Paper bot module and simulator.
- Live bot module and exchange execution adapter layer.
- Position/order persistence and reconciliation service.
- Bot control API endpoints and operator-facing dashboard controls.

