"""Step 2 technical filter implementation."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime

import pandas as pd

from app.clients.ccxt_market_data_client import CCXTMarketDataClient
from app.config.settings import Settings
from app.models.step2 import Step2Result
from app.scoring.step2_scorer import Step2Scorer
from app.utils.indicators import (
    adx,
    atr,
    bollinger_bands,
    clamp,
    ema,
    macd,
    ohlcv_to_dataframe,
    relative_slope_pct,
    rsi,
    stochastic_k,
)


LOGGER = logging.getLogger(__name__)


class TechnicalFilter(ABC):
    """Interface for Step 2 technical-entry validation."""

    @abstractmethod
    def evaluate(self, symbol: str, base_asset: str | None = None) -> Step2Result:
        """Evaluate technical suitability for entry."""


class CCXTTechnicalFilter(TechnicalFilter):
    """Step 2 filter based on OHLCV indicators."""

    def __init__(
        self,
        *,
        settings: Settings,
        market_data_client: CCXTMarketDataClient,
        scorer: Step2Scorer | None = None,
    ) -> None:
        self.settings = settings
        self.market_data_client = market_data_client
        self.scorer = scorer or Step2Scorer(settings)

    def evaluate(self, symbol: str, base_asset: str | None = None) -> Step2Result:
        base = base_asset or symbol.split("/")[0].upper()
        missing_technical_data: list[str] = []
        technical_reasoning: list[str] = []
        technical_snapshot: dict[str, float | int | str | bool | None] = {}
        fallback_used = False

        try:
            main_rows = self.market_data_client.fetch_ohlcv(
                symbol=symbol,
                timeframe=self.settings.technical_main_timeframe,
                limit=self.settings.technical_ohlcv_limit,
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Step2 ana timeframe OHLCV alinamadi %s: %s", symbol, exc)
            missing_technical_data.append("ohlcv_main_timeframe")
            technical_reasoning.append(f"ana timeframe OHLCV alinamadi: {exc}")
            return self._failed_result(
                symbol=symbol,
                base_asset=base,
                missing_technical_data=missing_technical_data,
                technical_reasoning=technical_reasoning,
                fallback_used=False,
            )

        df = ohlcv_to_dataframe(main_rows)
        if len(df) < self.settings.technical_min_ohlcv_rows:
            missing_technical_data.append("ohlcv_main_timeframe")
            technical_reasoning.append(
                "ana timeframe mum verisi yetersiz "
                f"({len(df)} < {self.settings.technical_min_ohlcv_rows})"
            )
            return self._failed_result(
                symbol=symbol,
                base_asset=base,
                missing_technical_data=missing_technical_data,
                technical_reasoning=technical_reasoning,
                fallback_used=False,
            )

        indicator_df = self._build_indicator_frame(df)
        if len(indicator_df) < self.settings.technical_min_ohlcv_rows:
            missing_technical_data.append("indicator_frame")
            technical_reasoning.append("indicator hesaplamasi icin yetersiz veri")
            return self._failed_result(
                symbol=symbol,
                base_asset=base,
                missing_technical_data=missing_technical_data,
                technical_reasoning=technical_reasoning,
                fallback_used=False,
            )

        recent_high = self._recent_high(indicator_df)
        latest = indicator_df.iloc[-1]
        previous = indicator_df.iloc[-2] if len(indicator_df) > 1 else None

        technical_snapshot.update(
            {
                "main_timeframe": self.settings.technical_main_timeframe,
                "close": self._safe_float(latest.get("close")),
                "ema_fast": self._safe_float(latest.get("ema_fast")),
                "ema_slow": self._safe_float(latest.get("ema_slow")),
                "ema_slow_slope_pct": relative_slope_pct(
                    indicator_df["ema_slow"],
                    self.settings.technical_ma_slope_lookback,
                ),
                "adx": self._safe_float(latest.get("adx")),
                "plus_di": self._safe_float(latest.get("plus_di")),
                "minus_di": self._safe_float(latest.get("minus_di")),
                "rsi": self._safe_float(latest.get("rsi")),
                "rsi_prev": self._safe_float(previous.get("rsi")) if previous is not None else None,
                "macd_line": self._safe_float(latest.get("macd_line")),
                "macd_signal": self._safe_float(latest.get("macd_signal")),
                "macd_hist": self._safe_float(latest.get("macd_hist")),
                "stoch_k": self._safe_float(latest.get("stoch_k")),
                "atr": self._safe_float(latest.get("atr")),
                "atr_pct": self._safe_float(latest.get("atr_pct")),
                "bb_upper": self._safe_float(latest.get("bb_upper")),
                "bb_mid": self._safe_float(latest.get("bb_mid")),
                "bb_lower": self._safe_float(latest.get("bb_lower")),
                "bb_width": self._safe_float(latest.get("bb_width")),
                "volume": self._safe_float(latest.get("volume")),
                "volume_sma": self._safe_float(latest.get("volume_sma")),
                "recent_volume_mean": self._safe_float(latest.get("recent_volume_mean")),
                "recent_high": recent_high,
            }
        )

        for metric_name, metric_value in technical_snapshot.items():
            if metric_name in {"main_timeframe"}:
                continue
            if metric_value is None:
                missing_technical_data.append(metric_name)

        trend_score, trend_flags, trend_reasons = self._evaluate_trend(technical_snapshot)
        momentum_score, momentum_flags, momentum_reasons = self._evaluate_momentum(technical_snapshot)
        volatility_score, volatility_flags, volatility_reasons = self._evaluate_volatility_structure(
            technical_snapshot
        )
        volume_score, volume_flags, volume_reasons = self._evaluate_volume(technical_snapshot)
        secondary_confirm = True
        if self.settings.technical_use_secondary_confirmation:
            secondary_confirm, secondary_reason, secondary_missing = self._evaluate_secondary_confirmation(symbol)
            if secondary_missing:
                missing_technical_data.extend(secondary_missing)
                fallback_used = True
            technical_reasoning.append(secondary_reason)

        technical_snapshot["secondary_confirm"] = secondary_confirm
        if self.settings.technical_use_secondary_confirmation:
            technical_snapshot["confirmation_timeframe"] = self.settings.technical_confirmation_timeframe

        entry_score, entry_flags, entry_reasons = self._evaluate_entry_pattern(
            technical_snapshot=technical_snapshot,
            trend_flags=trend_flags,
            volume_flags=volume_flags,
        )

        technical_reasoning.extend(trend_reasons)
        technical_reasoning.extend(momentum_reasons)
        technical_reasoning.extend(volatility_reasons)
        technical_reasoning.extend(volume_reasons)
        technical_reasoning.extend(entry_reasons)

        weak_setup = trend_score < 0.35 and momentum_score < 0.35
        hard_fail = (
            (volatility_flags["overextended"] and not entry_flags["breakout_with_volume"])
            or (volatility_flags["noisy_structure"] and trend_score < 0.50)
            or weak_setup
        )

        technical_flags = {
            **trend_flags,
            **momentum_flags,
            **volatility_flags,
            **volume_flags,
            **entry_flags,
            "secondary_confirm": secondary_confirm,
            "hard_fail": hard_fail,
        }

        sub_scores = {
            "trend": trend_score,
            "momentum": momentum_score,
            "volatility": volatility_score,
            "volume": volume_score,
            "entry": entry_score,
        }

        score_outcome = self.scorer.calculate(
            sub_scores=sub_scores,
            technical_flags=technical_flags,
            missing_technical_data=missing_technical_data,
        )
        technical_reasoning.extend(score_outcome.score_reasoning)

        return Step2Result(
            symbol=symbol,
            base_asset=base,
            timeframe=self.settings.technical_main_timeframe,
            confirmation_timeframe=(
                self.settings.technical_confirmation_timeframe
                if self.settings.technical_use_secondary_confirmation
                else None
            ),
            step2_score=score_outcome.step2_score,
            step2_pass=score_outcome.step2_pass,
            technical_reasoning=technical_reasoning,
            technical_snapshot=technical_snapshot,
            technical_flags=technical_flags,
            score_breakdown=score_outcome.score_breakdown,
            missing_technical_data=sorted(set(missing_technical_data)),
            fallback_used=fallback_used,
            generated_at=datetime.now(tz=UTC),
        )

    def _build_indicator_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        frame = df.copy()
        frame["ema_fast"] = ema(frame["close"], self.settings.technical_ma_fast_period)
        frame["ema_slow"] = ema(frame["close"], self.settings.technical_ma_slow_period)
        frame["rsi"] = rsi(frame["close"], self.settings.technical_rsi_period)
        macd_line, macd_signal, macd_hist = macd(
            frame["close"],
            self.settings.technical_macd_fast,
            self.settings.technical_macd_slow,
            self.settings.technical_macd_signal,
        )
        frame["macd_line"] = macd_line
        frame["macd_signal"] = macd_signal
        frame["macd_hist"] = macd_hist
        frame["atr"] = atr(
            frame["high"],
            frame["low"],
            frame["close"],
            self.settings.technical_atr_period,
        )
        frame["atr_pct"] = frame["atr"] / frame["close"].replace(0, pd.NA)
        adx_series, plus_di, minus_di = adx(
            frame["high"],
            frame["low"],
            frame["close"],
            self.settings.technical_adx_period,
        )
        frame["adx"] = adx_series
        frame["plus_di"] = plus_di
        frame["minus_di"] = minus_di
        bb_mid, bb_upper, bb_lower, bb_width = bollinger_bands(
            frame["close"],
            self.settings.technical_bbands_period,
            self.settings.technical_bbands_stddev,
        )
        frame["bb_mid"] = bb_mid
        frame["bb_upper"] = bb_upper
        frame["bb_lower"] = bb_lower
        frame["bb_width"] = bb_width
        frame["stoch_k"] = stochastic_k(
            frame["close"],
            frame["high"],
            frame["low"],
            self.settings.technical_stoch_period,
        )
        frame["volume_sma"] = frame["volume"].rolling(
            window=self.settings.technical_volume_ma_period,
            min_periods=self.settings.technical_volume_ma_period,
        ).mean()
        frame["recent_volume_mean"] = frame["volume"].rolling(window=3, min_periods=3).mean()
        return frame

    def _recent_high(self, frame: pd.DataFrame) -> float | None:
        lookback = self.settings.technical_breakout_lookback
        if len(frame) <= lookback:
            return None
        window = frame.iloc[-(lookback + 1) : -1]
        if window.empty:
            return None
        return self._safe_float(window["high"].max())

    def _evaluate_trend(
        self,
        snapshot: dict[str, float | int | str | bool | None],
    ) -> tuple[float, dict[str, bool], list[str]]:
        close = self._float_or_none(snapshot.get("close"))
        ema_fast = self._float_or_none(snapshot.get("ema_fast"))
        ema_slow = self._float_or_none(snapshot.get("ema_slow"))
        adx_value = self._float_or_none(snapshot.get("adx"))
        slope_pct = self._float_or_none(snapshot.get("ema_slow_slope_pct"))

        close_above_fast = self._safe_compare(close, ema_fast, ">")
        close_above_slow = self._safe_compare(close, ema_slow, ">")
        ma_alignment = self._safe_compare(ema_fast, ema_slow, ">")

        slope_score = 0.0
        if slope_pct is not None:
            slope_score = self._scaled_score(
                value=slope_pct,
                min_value=self.settings.technical_ma_slope_min_pct,
                strong_value=self.settings.technical_ma_slope_good_pct,
            )
        adx_score = 0.0
        if adx_value is not None:
            adx_score = self._scaled_score(
                value=adx_value,
                min_value=self.settings.technical_adx_min,
                strong_value=self.settings.technical_adx_strong,
            )

        trend_score = (
            0.20 * float(close_above_fast)
            + 0.20 * float(close_above_slow)
            + 0.20 * float(ma_alignment)
            + 0.20 * slope_score
            + 0.20 * adx_score
        )

        flags = {
            "trend_ok": trend_score >= 0.60,
            "close_above_fast_ma": close_above_fast,
            "close_above_slow_ma": close_above_slow,
            "ma_alignment_ok": ma_alignment,
            "adx_ok": adx_value is not None and adx_value >= self.settings.technical_adx_min,
            "ma_slope_ok": slope_pct is not None and slope_pct >= self.settings.technical_ma_slope_min_pct,
        }
        reasons = [f"trend skoru: {trend_score:.2f}"]
        return clamp(trend_score, 0.0, 1.0), flags, reasons

    def _evaluate_momentum(
        self,
        snapshot: dict[str, float | int | str | bool | None],
    ) -> tuple[float, dict[str, bool], list[str]]:
        rsi_value = self._float_or_none(snapshot.get("rsi"))
        macd_hist = self._float_or_none(snapshot.get("macd_hist"))
        macd_line = self._float_or_none(snapshot.get("macd_line"))
        macd_signal = self._float_or_none(snapshot.get("macd_signal"))
        stoch_k_value = self._float_or_none(snapshot.get("stoch_k"))

        rsi_score = 0.0
        if rsi_value is not None:
            if self.settings.technical_rsi_bullish_min <= rsi_value <= self.settings.technical_rsi_bullish_max:
                rsi_score = 1.0
            elif rsi_value < self.settings.technical_rsi_bullish_min:
                rsi_score = clamp(rsi_value / self.settings.technical_rsi_bullish_min, 0.0, 1.0)
            elif rsi_value <= self.settings.technical_rsi_extreme:
                denom = self.settings.technical_rsi_extreme - self.settings.technical_rsi_bullish_max
                if denom > 0:
                    rsi_score = clamp(
                        1 - ((rsi_value - self.settings.technical_rsi_bullish_max) / denom),
                        0.0,
                        1.0,
                    )

        macd_score = 0.0
        if macd_line is not None and macd_signal is not None and macd_hist is not None:
            if macd_line > macd_signal and macd_hist > 0:
                macd_score = 1.0
            elif macd_hist > 0:
                macd_score = 0.60
            elif macd_line > macd_signal:
                macd_score = 0.45

        stoch_score = 0.0
        if stoch_k_value is not None:
            if (
                self.settings.technical_stoch_bullish_min
                <= stoch_k_value
                <= self.settings.technical_stoch_overbought
            ):
                stoch_score = 1.0
            elif stoch_k_value < self.settings.technical_stoch_bullish_min:
                stoch_score = clamp(stoch_k_value / self.settings.technical_stoch_bullish_min, 0.0, 1.0)
            else:
                stoch_score = 0.25

        momentum_score = 0.45 * rsi_score + 0.40 * macd_score + 0.15 * stoch_score
        flags = {
            "momentum_ok": momentum_score >= 0.55,
            "rsi_ok": rsi_value is not None and self.settings.technical_rsi_bullish_min <= rsi_value <= self.settings.technical_rsi_extreme,
            "macd_ok": macd_line is not None and macd_signal is not None and macd_line > macd_signal and (macd_hist or 0) > 0,
            "stoch_ok": stoch_k_value is not None and stoch_k_value >= self.settings.technical_stoch_bullish_min,
            "rsi_extreme": rsi_value is not None and rsi_value >= self.settings.technical_rsi_extreme,
        }
        reasons = [f"momentum skoru: {momentum_score:.2f}"]
        return clamp(momentum_score, 0.0, 1.0), flags, reasons

    def _evaluate_volatility_structure(
        self,
        snapshot: dict[str, float | int | str | bool | None],
    ) -> tuple[float, dict[str, bool], list[str]]:
        atr_pct = self._float_or_none(snapshot.get("atr_pct"))
        bb_width = self._float_or_none(snapshot.get("bb_width"))
        close = self._float_or_none(snapshot.get("close"))
        bb_upper = self._float_or_none(snapshot.get("bb_upper"))
        adx_value = self._float_or_none(snapshot.get("adx"))

        atr_score = 0.0
        if atr_pct is not None:
            if self.settings.technical_atr_pct_min <= atr_pct <= self.settings.technical_atr_pct_max:
                atr_score = 1.0
            elif atr_pct < self.settings.technical_atr_pct_min:
                atr_score = clamp(atr_pct / self.settings.technical_atr_pct_min, 0.0, 1.0)
            else:
                excess_ratio = (atr_pct - self.settings.technical_atr_pct_max) / self.settings.technical_atr_pct_max
                atr_score = clamp(1 - excess_ratio, 0.0, 1.0)

        bb_state_score = 0.85
        compressed = False
        expansion = False
        if bb_width is not None:
            compressed = bb_width <= self.settings.technical_bb_width_compression_max
            expansion = bb_width >= self.settings.technical_bb_width_expansion_min
            if expansion:
                bb_state_score = 1.0
            elif compressed:
                bb_state_score = 0.80

        overextended = False
        if close is not None and bb_upper is not None:
            overextended = close > bb_upper * (1 + self.settings.technical_overextended_above_upper_pct)

        extension_score = 0.0 if overextended else 1.0
        volatility_score = 0.45 * atr_score + 0.25 * bb_state_score + 0.30 * extension_score
        noisy_structure = bool(
            atr_pct is not None
            and adx_value is not None
            and atr_pct > self.settings.technical_atr_pct_max
            and adx_value < self.settings.technical_adx_min
        )

        flags = {
            "volatility_ok": volatility_score >= 0.50 and not overextended,
            "overextended": overextended,
            "compressed": compressed,
            "expansion": expansion,
            "noisy_structure": noisy_structure,
        }
        reasons = [f"volatilite/struktur skoru: {volatility_score:.2f}"]
        return clamp(volatility_score, 0.0, 1.0), flags, reasons

    def _evaluate_volume(
        self,
        snapshot: dict[str, float | int | str | bool | None],
    ) -> tuple[float, dict[str, bool], list[str]]:
        volume = self._float_or_none(snapshot.get("volume"))
        volume_sma = self._float_or_none(snapshot.get("volume_sma"))
        recent_volume_mean = self._float_or_none(snapshot.get("recent_volume_mean"))

        volume_ratio = 0.0
        recent_ratio = 0.0
        if volume is not None and volume_sma is not None and volume_sma > 0:
            volume_ratio = volume / volume_sma
        if recent_volume_mean is not None and volume_sma is not None and volume_sma > 0:
            recent_ratio = recent_volume_mean / volume_sma

        best_ratio = max(volume_ratio, recent_ratio)
        volume_score = self._scaled_score(
            value=best_ratio,
            min_value=self.settings.technical_volume_ratio_min,
            strong_value=self.settings.technical_volume_ratio_strong,
        )

        flags = {
            "volume_ok": best_ratio >= self.settings.technical_volume_ratio_min,
            "volume_spike": best_ratio >= self.settings.technical_volume_ratio_strong,
        }
        reasons = [f"hacim skoru: {volume_score:.2f} (oran {best_ratio:.2f})"]
        snapshot["volume_ratio"] = round(best_ratio, 4)
        return clamp(volume_score, 0.0, 1.0), flags, reasons

    def _evaluate_entry_pattern(
        self,
        *,
        technical_snapshot: dict[str, float | int | str | bool | None],
        trend_flags: dict[str, bool],
        volume_flags: dict[str, bool],
    ) -> tuple[float, dict[str, bool], list[str]]:
        close = self._float_or_none(technical_snapshot.get("close"))
        recent_high = self._float_or_none(technical_snapshot.get("recent_high"))
        ema_fast = self._float_or_none(technical_snapshot.get("ema_fast"))
        ema_slow = self._float_or_none(technical_snapshot.get("ema_slow"))
        rsi_value = self._float_or_none(technical_snapshot.get("rsi"))
        rsi_prev = self._float_or_none(technical_snapshot.get("rsi_prev"))
        macd_hist = self._float_or_none(technical_snapshot.get("macd_hist"))
        secondary_confirm = bool(technical_snapshot.get("secondary_confirm", True))

        breakout = False
        if close is not None and recent_high is not None:
            breakout = close > recent_high * (1 + self.settings.technical_breakout_buffer_pct)

        pullback_distance_ok = False
        distance_pct: float | None = None
        if close is not None and ema_fast is not None and ema_fast > 0:
            distance_pct = abs(close - ema_fast) / ema_fast
            pullback_distance_ok = distance_pct <= self.settings.technical_pullback_tolerance_pct
            technical_snapshot["pullback_distance_pct"] = round(distance_pct, 6)

        stoch_k_value = self._float_or_none(technical_snapshot.get("stoch_k"))
        breakout_distance_ok = bool(
            distance_pct is not None
            and distance_pct <= (self.settings.technical_pullback_tolerance_pct * 1.25)
        )
        breakout_overheated = bool(
            (rsi_value is not None and rsi_value >= self.settings.technical_rsi_extreme)
            or (
                stoch_k_value is not None
                and stoch_k_value >= min(100.0, self.settings.technical_stoch_overbought + 10.0)
            )
        )
        breakout_with_volume = bool(
            breakout
            and volume_flags.get("volume_ok", False)
            and trend_flags.get("adx_ok", False)
            and breakout_distance_ok
            and not breakout_overheated
        )
        continuation_supported = bool(
            volume_flags.get("volume_ok", False) and trend_flags.get("adx_ok", False)
        )

        trend_continuation = bool(
            trend_flags.get("trend_ok", False)
            and close is not None
            and ema_fast is not None
            and ema_slow is not None
            and close > ema_fast > ema_slow
            and pullback_distance_ok
            and rsi_value is not None
            and rsi_value >= self.settings.technical_rsi_bullish_min
            and (rsi_value < self.settings.technical_rsi_extreme)
            and macd_hist is not None
            and macd_hist >= 0
            and continuation_supported
            and secondary_confirm
            and technical_snapshot.get("pullback_distance_pct") is not None
            and float(technical_snapshot["pullback_distance_pct"])
            <= (self.settings.technical_pullback_tolerance_pct * 0.5)
        )

        reversal_support = False

        entry_signal = breakout_with_volume or trend_continuation or reversal_support
        entry_score = max(
            1.0 if breakout_with_volume else 0.0,
            0.70 if trend_continuation else 0.0,
            0.50 if reversal_support else 0.0,
        )

        flags = {
            "entry_signal": entry_signal,
            "breakout": breakout,
            "breakout_with_volume": breakout_with_volume,
            "breakout_distance_ok": breakout_distance_ok,
            "breakout_overheated": breakout_overheated,
            "continuation_supported": continuation_supported,
            "trend_continuation": trend_continuation,
            "reversal_support": reversal_support,
        }
        reasons = [f"entry skoru: {entry_score:.2f}"]
        return entry_score, flags, reasons

    def _evaluate_secondary_confirmation(self, symbol: str) -> tuple[bool, str, list[str]]:
        missing: list[str] = []
        try:
            secondary_rows = self.market_data_client.fetch_ohlcv(
                symbol=symbol,
                timeframe=self.settings.technical_confirmation_timeframe,
                limit=self.settings.technical_ohlcv_limit,
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.info("Step2 secondary timeframe fallback (%s): %s", symbol, exc)
            missing.append("secondary_timeframe_ohlcv")
            return False, "secondary timeframe verisi alinamadi, fallback uygulandi", missing

        secondary_df = ohlcv_to_dataframe(secondary_rows)
        if len(secondary_df) < self.settings.technical_min_ohlcv_rows:
            missing.append("secondary_timeframe_ohlcv")
            return False, "secondary timeframe verisi yetersiz, fallback uygulandi", missing

        secondary_frame = self._build_indicator_frame(secondary_df)
        latest = secondary_frame.iloc[-1]
        close = self._safe_float(latest.get("close"))
        ema_fast = self._safe_float(latest.get("ema_fast"))
        ema_slow = self._safe_float(latest.get("ema_slow"))
        rsi_value = self._safe_float(latest.get("rsi"))
        macd_hist = self._safe_float(latest.get("macd_hist"))

        secondary_confirm = bool(
            close is not None
            and ema_fast is not None
            and ema_slow is not None
            and close > ema_slow
            and ema_fast >= ema_slow
            and rsi_value is not None
            and rsi_value >= self.settings.technical_rsi_bullish_min
            and macd_hist is not None
            and macd_hist >= -0.000001
        )
        if secondary_confirm:
            return True, "secondary timeframe onayi pozitif", missing
        return False, "secondary timeframe onayi zayif", missing

    def _failed_result(
        self,
        *,
        symbol: str,
        base_asset: str,
        missing_technical_data: list[str],
        technical_reasoning: list[str],
        fallback_used: bool,
    ) -> Step2Result:
        return Step2Result(
            symbol=symbol,
            base_asset=base_asset,
            timeframe=self.settings.technical_main_timeframe,
            confirmation_timeframe=(
                self.settings.technical_confirmation_timeframe
                if self.settings.technical_use_secondary_confirmation
                else None
            ),
            step2_score=0.0,
            step2_pass=False,
            technical_reasoning=technical_reasoning,
            technical_snapshot={"main_timeframe": self.settings.technical_main_timeframe},
            technical_flags={"hard_fail": True, "entry_signal": False},
            score_breakdown={},
            missing_technical_data=sorted(set(missing_technical_data)),
            fallback_used=fallback_used,
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
    def _safe_compare(left: float | None, right: float | None, operator: str) -> bool:
        if left is None or right is None:
            return False
        if operator == ">":
            return left > right
        if operator == "<":
            return left < right
        return False

    @staticmethod
    def _scaled_score(value: float | None, min_value: float, strong_value: float) -> float:
        if value is None:
            return 0.0
        if strong_value <= min_value:
            return 1.0 if value >= min_value else 0.0
        return clamp((value - min_value) / (strong_value - min_value), 0.0, 1.0)


class TechnicalFilterPlaceholder(TechnicalFilter):
    """Backward-compatible placeholder used by Step1-only runner."""

    def evaluate(self, symbol: str, base_asset: str | None = None) -> Step2Result:
        base = base_asset or symbol.split("/")[0].upper()
        return Step2Result(
            symbol=symbol,
            base_asset=base,
            timeframe="n/a",
            confirmation_timeframe=None,
            step2_score=0,
            step2_pass=False,
            technical_reasoning=[f"Step 2 aktif degil: {symbol}"],
            technical_snapshot={},
            technical_flags={"hard_fail": False, "entry_signal": False},
            score_breakdown={},
            missing_technical_data=["step2_disabled"],
            fallback_used=True,
            generated_at=datetime.now(tz=UTC),
        )
