"""Step 3 market regime/risk filter implementation."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime

import pandas as pd

from app.clients.ccxt_market_data_client import CCXTMarketDataClient
from app.config.settings import Settings
from app.models.step3 import Step3Result
from app.scoring.step3_scorer import Step3Scorer
from app.utils.indicators import adx, atr, clamp, ema, ohlcv_to_dataframe, relative_slope_pct


LOGGER = logging.getLogger(__name__)


class DerivativesRiskAdapter(ABC):
    """Optional derivatives risk metrics interface."""

    @abstractmethod
    def fetch(self, symbol: str) -> tuple[dict[str, float], list[str], bool]:
        """Return available metrics, unavailable metric names, and fallback flag."""


class CCXTDerivativesRiskAdapter(DerivativesRiskAdapter):
    """Best-effort derivatives adapter using CCXT supported methods."""

    def __init__(self, market_data_client: CCXTMarketDataClient) -> None:
        self.market_data_client = market_data_client

    def fetch(self, symbol: str) -> tuple[dict[str, float], list[str], bool]:
        metrics: dict[str, float] = {}
        unavailable: list[str] = []
        fallback_used = False

        funding_rate = self.market_data_client.fetch_funding_rate(symbol=symbol)
        if funding_rate is None:
            unavailable.append("funding_rate")
            fallback_used = True
        else:
            metrics["funding_rate"] = funding_rate

        open_interest = self.market_data_client.fetch_open_interest(symbol=symbol)
        if open_interest is None:
            unavailable.append("open_interest")
            fallback_used = True
        else:
            metrics["open_interest"] = open_interest

        # CCXT spot/perp APIs rarely provide reliable liquidation pressure directly.
        unavailable.append("liquidation_risk")
        fallback_used = True
        return metrics, unavailable, fallback_used


class MarketRegimeFilter(ABC):
    """Interface for Step 3 global market-risk validation."""

    @abstractmethod
    def evaluate(self, symbol: str, market_symbols: list[str] | None = None) -> Step3Result:
        """Evaluate market regime and return coin-level Step 3 decision."""


class CCXTMarketRegimeFilter(MarketRegimeFilter):
    """Step 3 filter driven by BTC regime and market risk proxies."""

    def __init__(
        self,
        *,
        settings: Settings,
        market_data_client: CCXTMarketDataClient,
        scorer: Step3Scorer | None = None,
        derivatives_adapter: DerivativesRiskAdapter | None = None,
    ) -> None:
        self.settings = settings
        self.market_data_client = market_data_client
        self.scorer = scorer or Step3Scorer(settings)
        self.derivatives_adapter = derivatives_adapter or CCXTDerivativesRiskAdapter(market_data_client)

    def evaluate(self, symbol: str, market_symbols: list[str] | None = None) -> Step3Result:
        base_asset = symbol.split("/")[0].upper()
        regime_reasoning: list[str] = []
        regime_snapshot: dict[str, float | int | str | bool | None] = {}
        unavailable_risk_metrics: list[str] = []
        fallback_used = False

        btc_frame = self._fetch_btc_regime_frame()
        if btc_frame is None:
            return self._danger_result(
                symbol=symbol,
                base_asset=base_asset,
                regime_reasoning=["BTC rejim verisi alinamadi, risk veto uygulandi"],
                unavailable_risk_metrics=["btc_regime_data"],
                fallback_used=True,
            )

        latest = btc_frame.iloc[-1]
        regime_snapshot.update(
            {
                "btc_symbol": self.settings.regime_btc_symbol,
                "regime_timeframe": self.settings.regime_timeframe,
                "btc_close": self._safe_float(latest.get("close")),
                "btc_ema_fast": self._safe_float(latest.get("ema_fast")),
                "btc_ema_slow": self._safe_float(latest.get("ema_slow")),
                "btc_adx": self._safe_float(latest.get("adx")),
                "btc_plus_di": self._safe_float(latest.get("plus_di")),
                "btc_minus_di": self._safe_float(latest.get("minus_di")),
                "btc_atr": self._safe_float(latest.get("atr")),
                "btc_atr_pct": self._safe_float(latest.get("atr_pct")),
                "btc_slope_pct": relative_slope_pct(
                    btc_frame["ema_slow"],
                    self.settings.regime_btc_slope_lookback,
                ),
            }
        )

        trend_score, trend_reason = self._evaluate_btc_trend(regime_snapshot)
        volatility_score, danger_flag, volatility_reason, drawdown_pct = self._evaluate_btc_volatility(
            btc_frame=btc_frame,
            regime_snapshot=regime_snapshot,
        )
        regime_snapshot["btc_drawdown_pct"] = drawdown_pct
        regime_reasoning.append(trend_reason)
        regime_reasoning.append(volatility_reason)

        breadth_score, breadth_reason, breadth_snapshot, breadth_fallback, breadth_unavailable = self._evaluate_breadth(
            market_symbols
        )
        regime_snapshot.update(breadth_snapshot)
        regime_reasoning.append(breadth_reason)
        fallback_used = fallback_used or breadth_fallback
        unavailable_risk_metrics.extend(breadth_unavailable)

        derivatives_score, derivatives_reason, derivatives_snapshot, derivatives_unavailable, derivatives_fallback = (
            self._evaluate_derivatives()
        )
        regime_snapshot.update(derivatives_snapshot)
        regime_reasoning.append(derivatives_reason)
        fallback_used = fallback_used or derivatives_fallback
        unavailable_risk_metrics.extend(derivatives_unavailable)

        sub_scores = {
            "trend": trend_score,
            "volatility": volatility_score,
            "breadth": breadth_score,
            "derivatives": derivatives_score,
        }
        score_outcome = self.scorer.calculate(
            sub_scores=sub_scores,
            danger_flag=danger_flag,
            fallback_used=fallback_used,
        )
        regime_reasoning.extend(score_outcome.score_reasoning)

        return Step3Result(
            symbol=symbol,
            base_asset=base_asset,
            step3_pass=score_outcome.step3_pass,
            regime_status=score_outcome.regime_status,
            regime_score=score_outcome.regime_score,
            regime_reasoning=regime_reasoning,
            regime_snapshot=regime_snapshot,
            score_breakdown=score_outcome.score_breakdown,
            fallback_used=fallback_used,
            unavailable_risk_metrics=sorted(set(unavailable_risk_metrics)),
            generated_at=datetime.now(tz=UTC),
        )

    def _fetch_btc_regime_frame(self) -> pd.DataFrame | None:
        try:
            btc_rows = self.market_data_client.fetch_ohlcv(
                symbol=self.settings.regime_btc_symbol,
                timeframe=self.settings.regime_timeframe,
                limit=self.settings.regime_ohlcv_limit,
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Step3 BTC OHLCV fetch failed: %s", exc)
            return None

        btc_df = ohlcv_to_dataframe(btc_rows)
        if len(btc_df) < self.settings.regime_min_ohlcv_rows:
            LOGGER.warning(
                "Step3 BTC OHLCV insufficient rows: %s < %s",
                len(btc_df),
                self.settings.regime_min_ohlcv_rows,
            )
            return None

        btc_df["ema_fast"] = ema(btc_df["close"], self.settings.regime_btc_ma_fast_period)
        btc_df["ema_slow"] = ema(btc_df["close"], self.settings.regime_btc_ma_slow_period)
        adx_series, plus_di, minus_di = adx(
            btc_df["high"],
            btc_df["low"],
            btc_df["close"],
            self.settings.regime_adx_period,
        )
        btc_df["adx"] = adx_series
        btc_df["plus_di"] = plus_di
        btc_df["minus_di"] = minus_di
        btc_df["atr"] = atr(
            btc_df["high"],
            btc_df["low"],
            btc_df["close"],
            self.settings.regime_atr_period,
        )
        btc_df["atr_pct"] = btc_df["atr"] / btc_df["close"].replace(0, pd.NA)
        return btc_df

    def _evaluate_btc_trend(self, snapshot: dict[str, float | int | str | bool | None]) -> tuple[float, str]:
        close = self._float_or_none(snapshot.get("btc_close"))
        ema_fast = self._float_or_none(snapshot.get("btc_ema_fast"))
        ema_slow = self._float_or_none(snapshot.get("btc_ema_slow"))
        slope_pct = self._float_or_none(snapshot.get("btc_slope_pct"))
        adx_value = self._float_or_none(snapshot.get("btc_adx"))

        close_above_fast = bool(close is not None and ema_fast is not None and close > ema_fast)
        close_above_slow = bool(close is not None and ema_slow is not None and close > ema_slow)
        ma_alignment = bool(ema_fast is not None and ema_slow is not None and ema_fast > ema_slow)

        slope_score = self._scaled_score(
            value=slope_pct,
            min_value=self.settings.regime_btc_slope_min_pct,
            strong_value=self.settings.regime_btc_slope_good_pct,
        )
        adx_score = self._scaled_score(
            value=adx_value,
            min_value=self.settings.regime_adx_min,
            strong_value=self.settings.regime_adx_strong,
        )

        trend_score = (
            0.25 * float(close_above_fast)
            + 0.25 * float(close_above_slow)
            + 0.20 * float(ma_alignment)
            + 0.15 * slope_score
            + 0.15 * adx_score
        )
        reason = f"BTC trend skoru: {trend_score:.2f}"
        return clamp(trend_score, 0.0, 1.0), reason

    def _evaluate_btc_volatility(
        self,
        *,
        btc_frame: pd.DataFrame,
        regime_snapshot: dict[str, float | int | str | bool | None],
    ) -> tuple[float, bool, str, float | None]:
        atr_pct = self._float_or_none(regime_snapshot.get("btc_atr_pct"))
        close = self._float_or_none(regime_snapshot.get("btc_close"))

        drawdown_pct: float | None = None
        lookback_window = btc_frame["high"].tail(self.settings.regime_drawdown_lookback)
        if close is not None and not lookback_window.empty:
            recent_high = float(lookback_window.max())
            if recent_high > 0:
                drawdown_pct = (recent_high - close) / recent_high

        atr_stability_score = 0.5
        if atr_pct is not None and self.settings.regime_atr_danger_pct > 0:
            atr_stability_score = clamp(1 - (atr_pct / self.settings.regime_atr_danger_pct), 0.0, 1.0)

        drawdown_stability_score = 0.5
        if drawdown_pct is not None and self.settings.regime_drawdown_danger_pct > 0:
            drawdown_stability_score = clamp(
                1 - (drawdown_pct / self.settings.regime_drawdown_danger_pct),
                0.0,
                1.0,
            )

        volatility_score = 0.60 * atr_stability_score + 0.40 * drawdown_stability_score

        danger_flag = bool(
            (atr_pct is not None and atr_pct >= self.settings.regime_atr_danger_pct)
            or (drawdown_pct is not None and drawdown_pct >= self.settings.regime_drawdown_danger_pct)
        )
        reason = f"BTC volatilite skoru: {volatility_score:.2f} (danger={danger_flag})"
        return clamp(volatility_score, 0.0, 1.0), danger_flag, reason, drawdown_pct

    def _evaluate_breadth(
        self,
        market_symbols: list[str] | None,
    ) -> tuple[float, str, dict[str, float | int | str | bool | None], bool, list[str]]:
        snapshot: dict[str, float | int | str | bool | None] = {}
        unavailable: list[str] = []
        if not self.settings.regime_breadth_enabled:
            snapshot["breadth_enabled"] = False
            return 0.5, "market breadth devre disi", snapshot, False, unavailable

        symbols = [item for item in (market_symbols or []) if item != self.settings.regime_btc_symbol]
        symbols = symbols[: self.settings.regime_breadth_symbol_count]
        if not symbols:
            unavailable.append("market_breadth")
            snapshot["breadth_sample_count"] = 0
            return 0.40, "market breadth sembol listesi yok, temkinli fallback", snapshot, True, unavailable

        strong_count = 0
        sample_count = 0
        for current_symbol in symbols:
            try:
                rows = self.market_data_client.fetch_ohlcv(
                    symbol=current_symbol,
                    timeframe=self.settings.regime_breadth_timeframe,
                    limit=self.settings.regime_ohlcv_limit,
                )
            except Exception:
                continue

            frame = ohlcv_to_dataframe(rows)
            if len(frame) < self.settings.regime_min_ohlcv_rows:
                continue

            frame["breadth_ema_fast"] = ema(frame["close"], self.settings.regime_breadth_fast_period)
            frame["breadth_ema_slow"] = ema(frame["close"], self.settings.regime_breadth_slow_period)
            latest = frame.iloc[-1]
            close = self._safe_float(latest.get("close"))
            ema_fast = self._safe_float(latest.get("breadth_ema_fast"))
            ema_slow = self._safe_float(latest.get("breadth_ema_slow"))
            if close is None or ema_fast is None or ema_slow is None:
                continue

            sample_count += 1
            if close > ema_fast > ema_slow:
                strong_count += 1

        if sample_count < self.settings.regime_breadth_min_samples:
            unavailable.append("market_breadth")
            snapshot["breadth_sample_count"] = sample_count
            return 0.40, "market breadth ornek sayisi dusuk, temkinli fallback", snapshot, True, unavailable

        breadth_ratio = strong_count / sample_count
        bearish = self.settings.regime_breadth_bearish_ratio
        bullish = self.settings.regime_breadth_bullish_ratio
        breadth_score = self._scaled_score(breadth_ratio, bearish, bullish)

        snapshot["breadth_enabled"] = True
        snapshot["breadth_sample_count"] = sample_count
        snapshot["breadth_strong_count"] = strong_count
        snapshot["breadth_ratio"] = round(breadth_ratio, 4)
        reason = f"market breadth skoru: {breadth_score:.2f} (oran {breadth_ratio:.2f})"
        return breadth_score, reason, snapshot, False, unavailable

    def _evaluate_derivatives(
        self,
    ) -> tuple[float, str, dict[str, float | int | str | bool | None], list[str], bool]:
        snapshot: dict[str, float | int | str | bool | None] = {}
        if not self.settings.regime_derivatives_enabled:
            return (
                self.settings.regime_derivatives_neutral_score,
                "derivatives metrikleri devre disi (neutral skor)",
                snapshot,
                [],
                False,
            )

        symbol = self.settings.regime_derivatives_symbol or self.settings.regime_btc_symbol
        metrics, unavailable, fallback_used = self.derivatives_adapter.fetch(symbol)
        snapshot["derivatives_symbol"] = symbol
        snapshot["funding_rate"] = metrics.get("funding_rate")
        snapshot["open_interest"] = metrics.get("open_interest")

        metric_scores: list[float] = []
        funding_rate = metrics.get("funding_rate")
        if funding_rate is not None and self.settings.regime_funding_abs_max > 0:
            funding_score = clamp(
                1 - (abs(funding_rate) / self.settings.regime_funding_abs_max),
                0.0,
                1.0,
            )
            metric_scores.append(funding_score)

        open_interest = metrics.get("open_interest")
        if open_interest is not None:
            # Without OI history, existence is neutral rather than bullish.
            metric_scores.append(0.50 if open_interest > 0 else 0.45)

        if metric_scores:
            derivatives_score = sum(metric_scores) / len(metric_scores)
        else:
            derivatives_score = self.settings.regime_derivatives_neutral_score
            fallback_used = True

        reason = f"derivatives skoru: {derivatives_score:.2f}"
        if unavailable:
            reason += f" (eksik: {','.join(unavailable)})"

        return derivatives_score, reason, snapshot, unavailable, fallback_used

    def _danger_result(
        self,
        *,
        symbol: str,
        base_asset: str,
        regime_reasoning: list[str],
        unavailable_risk_metrics: list[str],
        fallback_used: bool,
    ) -> Step3Result:
        return Step3Result(
            symbol=symbol,
            base_asset=base_asset,
            step3_pass=False,
            regime_status="DANGER",
            regime_score=0.0,
            regime_reasoning=regime_reasoning,
            regime_snapshot={"btc_symbol": self.settings.regime_btc_symbol},
            score_breakdown={},
            fallback_used=fallback_used,
            unavailable_risk_metrics=sorted(set(unavailable_risk_metrics)),
            generated_at=datetime.now(tz=UTC),
        )

    @staticmethod
    def _safe_float(value: object) -> float | None:
        try:
            if value is None or pd.isna(value):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _float_or_none(value: object) -> float | None:
        if isinstance(value, (float, int)):
            return float(value)
        return None

    @staticmethod
    def _scaled_score(value: float | None, min_value: float, strong_value: float) -> float:
        if value is None:
            return 0.0
        if strong_value <= min_value:
            return 1.0 if value >= min_value else 0.0
        return clamp((value - min_value) / (strong_value - min_value), 0.0, 1.0)


class MarketRegimeFilterPlaceholder(MarketRegimeFilter):
    """Backward-compatible placeholder for Step1-only runner."""

    def evaluate(self, symbol: str, market_symbols: list[str] | None = None) -> Step3Result:
        base_asset = symbol.split("/")[0].upper()
        return Step3Result(
            symbol=symbol,
            base_asset=base_asset,
            step3_pass=False,
            regime_status="NEUTRAL",
            regime_score=0.0,
            regime_reasoning=["Step 3 aktif degil"],
            regime_snapshot={},
            score_breakdown={},
            fallback_used=True,
            unavailable_risk_metrics=["step3_disabled"],
            generated_at=datetime.now(tz=UTC),
        )
