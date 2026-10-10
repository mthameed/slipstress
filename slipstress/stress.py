"""Apply a slippage haircut to specific exit types in a trade log, then
recompute performance so you can see how much of your edge survives real
fills.

The core finding this tool is built around: slippage doesn't hit every
exit equally. A stop-loss or trailing-stop fires at a price level your
code *computed* -- by the time an order reaches the book, the market has
often already moved through it. A time-based or end-of-day exit fills at
whatever the market *actually is* right now, so it isn't haircut the same
way. Tag your exits by type and stress only the ones that are actually
exposed.
"""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

from .metrics import compute_pnl, performance_metrics, PerformanceMetrics

DEFAULT_STRESSED_EXIT_TYPES = ("stop_loss", "trailing_stop", "atr_stop")


def apply_slippage(trades: pd.DataFrame, slip_pct: float,
                    stressed_exit_types: tuple[str, ...] = DEFAULT_STRESSED_EXIT_TYPES) -> pd.DataFrame:
    """Returns a new trade log with exit_price haircut on the given exit
    types. Long-only: a worse fill on a sell is a *lower* exit price."""
    out = trades.copy()
    mask = out["exit_type"].isin(stressed_exit_types)
    out.loc[mask, "exit_price"] = out.loc[mask, "exit_price"] * (1 - slip_pct)
    return out


@dataclass
class StressResult:
    slip_pct: float
    stressed_exit_types: tuple[str, ...]
    baseline: PerformanceMetrics
    stressed: PerformanceMetrics

    def as_dict(self) -> dict:
        return {
            "slip_pct": self.slip_pct,
            "stressed_exit_types": list(self.stressed_exit_types),
            "baseline": self.baseline.as_dict(),
            "stressed": self.stressed.as_dict(),
        }


def run_stress_test(trades: pd.DataFrame, initial_equity: float, slip_pct: float,
                     stressed_exit_types: tuple[str, ...] = DEFAULT_STRESSED_EXIT_TYPES) -> StressResult:
    baseline_trades = compute_pnl(trades)
    stressed_trades = compute_pnl(apply_slippage(trades, slip_pct, stressed_exit_types))

    return StressResult(
        slip_pct=slip_pct,
        stressed_exit_types=stressed_exit_types,
        baseline=performance_metrics(baseline_trades, initial_equity),
        stressed=performance_metrics(stressed_trades, initial_equity),
    )
