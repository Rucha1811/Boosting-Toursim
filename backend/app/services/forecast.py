"""
Tourism demand prediction.

Modular design: forecasts come from an interchangeable "model" object.
- HeuristicModel : deterministic baseline built from live + historical data.
- SeasonalEnsemble: combines base rate, day-of-week multiplier, festival boost
  and hotel-occupancy signal; runs a small least-squares fit when enough
  history exists.

Models can be swapped later (e.g. gradient boosting / LSTM) without touching
the API layer — every model exposes `forecast(context) -> ForecastResult`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np


@dataclass
class ForecastContext:
    destination_id: int
    date: str
    event_name: str = ""
    is_festival: bool = False
    festival_peak_multiplier: float = 1.0
    historical: List[int] = field(default_factory=list)
    place_capacity: int = 0
    hotel_occupancy_pct: float = 0.0
    weather_bonus: float = 1.0


@dataclass
class ForecastResult:
    expected_visitors: int
    expected_peak_start: str
    expected_peak_end: str
    confidence: float
    method: str
    is_demo: bool = True


DAY_MULTIPLIERS = {"Mon": 0.86, "Tue": 0.88, "Wed": 0.9, "Thu": 0.92, "Fri": 1.05, "Sat": 1.28, "Sun": 1.22}
WEEKEND_PEAK = ("11:00", "19:00")
WEEKDAY_PEAK = ("17:00", "21:00")


class HeuristicModel:
    method = "heuristic-baseline"

    def forecast(self, ctx: ForecastContext) -> ForecastResult:
        base = _base_rate(ctx.historical)
        weekday_mult = _weekday_multiplier(ctx.date)
        festival_boost = ctx.festival_peak_multiplier if ctx.is_festival else 1.0
        occupancy_signal = 1.0 + max(0.0, (ctx.hotel_occupancy_pct - 65.0) / 100.0)
        season_mult = _seasonality(ctx.date)

        expected = int(base * weekday_mult * festival_boost * occupancy_signal * season_mult * ctx.weather_bonus)
        peak_start, peak_end = WEEKEND_PEAK if _is_weekend(ctx.date) else WEEKDAY_PEAK
        return ForecastResult(
            expected_visitors=expected,
            expected_peak_start=peak_start,
            expected_peak_end=peak_end,
            confidence=0.68,
            method=self.method,
        )


class SeasonalEnsembleModel:
    """Linear-regression style blend of signals against recent history."""

    method = "seasonal-ensemble"

    def fit(self, dates: List[str], counts: List[int]) -> Optional[np.ndarray]:
        if len(dates) < 14:
            return None
        X = np.array([_features(d) for d in dates])
        y = np.array(counts, dtype=float)
        try:
            Xd = np.c_[np.ones(len(X)), X]
            coef, *_ = np.linalg.lstsq(Xd, y, rcond=None)
            return coef
        except Exception:
            return None

    def forecast(self, ctx: ForecastContext) -> ForecastResult:
        base = _base_rate(ctx.historical)
        coef = self.fit([_d_str(i) for i in range(len(ctx.historical))], ctx.historical) if ctx.historical else None
        weekday_mult = _weekday_multiplier(ctx.date)
        festival_boost = ctx.festival_peak_multiplier if ctx.is_festival else 1.0
        occupancy_signal = 1.0 + max(0.0, (ctx.hotel_occupancy_pct - 65.0) / 100.0)
        season_mult = _seasonality(ctx.date)

        if coef is not None:
            x = _features(ctx.date)
            trend = float(coef @ np.array([1, x[0], x[1]]))
            expected = int(max(trend, base * 0.5) * weekday_mult * festival_boost * occupancy_signal * season_mult)
        else:
            expected = int(base * weekday_mult * festival_boost * occupancy_signal * season_mult)

        peak_start, peak_end = WEEKEND_PEAK if _is_weekend(ctx.date) else WEEKDAY_PEAK
        return ForecastResult(
            expected_visitors=max(expected, 25),
            expected_peak_start=peak_start,
            expected_peak_end=peak_end,
            confidence=0.74 if coef is not None else 0.66,
            method=self.method,
        )


class ForecastService:
    def __init__(self, model: Optional[object] = None, use_ensemble: bool = True):
        self.ensemble = SeasonalEnsembleModel() if (use_ensemble and _np_ok()) else HeuristicModel()
        self.heuristic = HeuristicModel()
        self.active = model or self.ensemble

    def forecast(self, ctx: ForecastContext) -> ForecastResult:
        try:
            return self.active.forecast(ctx)
        except Exception:
            return self.heuristic.forecast(ctx)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _np_ok() -> bool:
    return True


def _base_rate(history: List[int]) -> float:
    if history:
        return sum(history) / len(history)
    return 1200


def _parse(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return datetime.strptime(date_str, "%a")
    except Exception:
        return datetime.utcnow()


def _is_weekend(date_str: str) -> bool:
    return _parse(date_str).strftime("%a") in ("Sat", "Sun")


def _weekday_multiplier(date_str: str) -> float:
    return DAY_MULTIPLIERS.get(_parse(date_str).strftime("%a"), 1.0)


def _seasonality(date_str: str) -> float:
    """Rough seasonal profile: festival season (Sep-Nov) and winter tourism peak."""
    m = _parse(date_str).month
    if m in (10, 11, 12):
        return 1.35
    if m in (1, 2, 3):
        return 1.18
    if m in (6, 7, 8):
        return 0.78
    return 1.0


def _features(date_str: str) -> List[float]:
    dt = _parse(date_str)
    return [dt.weekday(), 1.0 if _is_weekend(date_str) else 0.0]


def _d_str(i: int) -> str:
    return (datetime(2026, 1, 1) + timedelta(days=i)).strftime("%Y-%m-%d")