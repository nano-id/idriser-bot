"""Technical indicator utilities."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def ohlcv_to_dataframe(ohlcv_rows: list[list[float]]) -> pd.DataFrame:
    """Convert CCXT OHLCV rows to normalized DataFrame."""
    if not ohlcv_rows:
        return pd.DataFrame(columns=OHLCV_COLUMNS)

    cleaned_rows = [row[:6] for row in ohlcv_rows if len(row) >= 6]
    if not cleaned_rows:
        return pd.DataFrame(columns=OHLCV_COLUMNS)

    df = pd.DataFrame(cleaned_rows, columns=OHLCV_COLUMNS)
    for column in ("open", "high", "low", "close", "volume"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True, errors="coerce")
    df = df.dropna(subset=["timestamp", "open", "high", "low", "close", "volume"])
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return df


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential moving average."""
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple moving average."""
    return series.rolling(window=period, min_periods=period).mean()


def rsi(series: pd.Series, period: int) -> pd.Series:
    """Relative Strength Index (Wilder-style smoothing)."""
    numeric_series = pd.to_numeric(series, errors="coerce")
    delta = numeric_series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series.fillna(50.0)


def macd(series: pd.Series, fast: int, slow: int, signal: int) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD line, signal line, and histogram."""
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """True range series."""
    prev_close = close.shift(1)
    range_1 = high - low
    range_2 = (high - prev_close).abs()
    range_3 = (low - prev_close).abs()
    return pd.concat([range_1, range_2, range_3], axis=1).max(axis=1)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> pd.Series:
    """Average True Range (Wilder-style smoothing)."""
    tr = true_range(high=high, low=low, close=close)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Average Directional Index and directional indicators."""
    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    tr = true_range(high=high, low=low, close=close)
    atr_series = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    plus_di = (
        100
        * plus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
        / atr_series.replace(0, pd.NA)
    )
    minus_di = (
        100
        * minus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
        / atr_series.replace(0, pd.NA)
    )
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)
    adx_series = dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    return adx_series.fillna(0), plus_di.fillna(0), minus_di.fillna(0)


def bollinger_bands(series: pd.Series, period: int, stddev: float) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Bollinger bands and width ratio."""
    mid = sma(series, period)
    std = series.rolling(window=period, min_periods=period).std(ddof=0)
    upper = mid + stddev * std
    lower = mid - stddev * std
    width = (upper - lower) / mid.replace(0, pd.NA)
    return mid, upper, lower, width


def stochastic_k(close: pd.Series, high: pd.Series, low: pd.Series, period: int) -> pd.Series:
    """Stochastic %K oscillator."""
    lowest_low = low.rolling(window=period, min_periods=period).min()
    highest_high = high.rolling(window=period, min_periods=period).max()
    denominator = (highest_high - lowest_low).replace(0, pd.NA)
    k = 100 * (close - lowest_low) / denominator
    return k.fillna(50)


def latest_valid(series: pd.Series) -> float | None:
    """Get the latest non-null numeric value from a Series."""
    cleaned = series.dropna()
    if cleaned.empty:
        return None
    return float(cleaned.iloc[-1])


def relative_slope_pct(series: pd.Series, lookback: int) -> float | None:
    """Return % slope using first and last points in lookback window."""
    cleaned = series.dropna()
    if cleaned.empty or len(cleaned) < lookback:
        return None

    window = cleaned.iloc[-lookback:]
    start = float(window.iloc[0])
    end = float(window.iloc[-1])
    if abs(start) < 1e-12:
        return None
    return (end - start) / abs(start)


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp value into [lower, upper]."""
    return max(lower, min(upper, value))


def ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> list[str]:
    """Return missing required columns from DataFrame."""
    missing: list[str] = []
    for column in required:
        if column not in df.columns:
            missing.append(column)
    return missing
