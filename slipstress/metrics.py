"""Generic backtest performance metrics -- Sharpe, CAGR, max drawdown,
profit factor, expectancy, win rate. Works on any trade log with a 'pnl'
column and an exit_date, independent of what strategy produced it.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd


def compute_pnl(trades: pd.DataFrame) -> pd.DataFrame:
    """Long-only cash P&L per trade, net of commission."""
    out = trades.copy()
    out["pnl"] = (out["exit_price"] - out["entry_price"]) * out["qty"] - out["commission"]
    return out


def build_equity_curve(trades: pd.DataFrame, initial_equity: float) -> pd.Series:
    """Daily equity curve built by cumulatively applying each trade's P&L
    on its exit date, forward-filled between trades. Position sizing and
    intraday timing aren't modeled -- this is the same simplification any
    trade-level (vs. tick-level) backtest report relies on."""
    by_day = trades.groupby(trades["exit_date"].dt.normalize())["pnl"].sum()
    full_index = pd.date_range(by_day.index.min(), by_day.index.max(), freq="D")
    daily_pnl = by_day.reindex(full_index, fill_value=0.0)
    equity = initial_equity + daily_pnl.cumsum()
    return equity


@dataclass
class PerformanceMetrics:
    num_trades: int
    total_return_pct: float
    cagr_pct: float
    sharpe: float
    max_drawdown_pct: float
    profit_factor: float
    win_rate_pct: float
    expectancy: float
    total_commission: float

    def as_dict(self) -> dict:
        return asdict(self)


def performance_metrics(trades: pd.DataFrame, initial_equity: float) -> PerformanceMetrics:
    if trades.empty:
        raise ValueError("No trades to evaluate.")

    equity = build_equity_curve(trades, initial_equity)
    final_equity = float(equity.iloc[-1])
    total_return_pct = (final_equity / initial_equity - 1.0) * 100.0

    days = max((equity.index[-1] - equity.index[0]).days, 1)
    years = days / 365.25
    cagr_pct = ((final_equity / initial_equity) ** (1.0 / years) - 1.0) * 100.0 if years > 0 else 0.0

    daily_returns = equity.pct_change().dropna()
    if daily_returns.std() > 0:
        sharpe = float(daily_returns.mean() / daily_returns.std() * np.sqrt(252))
    else:
        sharpe = 0.0

    running_max = equity.cummax()
    drawdown_pct = (equity - running_max) / running_max * 100.0
    max_drawdown_pct = float(drawdown_pct.min())

    wins = trades[trades["pnl"] > 0]["pnl"]
    losses = trades[trades["pnl"] <= 0]["pnl"]
    gross_profit = float(wins.sum())
    gross_loss = float(-losses.sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
    win_rate_pct = len(wins) / len(trades) * 100.0
    expectancy = float(trades["pnl"].mean())

    return PerformanceMetrics(
        num_trades=len(trades),
        total_return_pct=round(total_return_pct, 2),
        cagr_pct=round(cagr_pct, 2),
        sharpe=round(sharpe, 3),
        max_drawdown_pct=round(max_drawdown_pct, 2),
        profit_factor=round(profit_factor, 3) if profit_factor != float("inf") else profit_factor,
        win_rate_pct=round(win_rate_pct, 2),
        expectancy=round(expectancy, 2),
        total_commission=round(float(trades["commission"].sum()), 2),
    )
