import pandas as pd
import pytest
from slipstress.metrics import compute_pnl, performance_metrics


def _trades(rows):
    df = pd.DataFrame(rows)
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df["exit_date"] = pd.to_datetime(df["exit_date"])
    if "commission" not in df.columns:
        df["commission"] = 0.0
    return df


def test_compute_pnl_long_only():
    trades = _trades([
        {"symbol": "AAPL", "entry_date": "2026-01-01", "exit_date": "2026-01-05",
         "entry_price": 100.0, "exit_price": 110.0, "qty": 10, "exit_type": "target", "commission": 2.0},
    ])
    out = compute_pnl(trades)
    assert out["pnl"].iloc[0] == pytest.approx(10 * (110.0 - 100.0) - 2.0)


def test_performance_metrics_all_wins():
    trades = _trades([
        {"symbol": "AAPL", "entry_date": "2026-01-01", "exit_date": "2026-01-05",
         "entry_price": 100.0, "exit_price": 110.0, "qty": 10, "exit_type": "target"},
        {"symbol": "MSFT", "entry_date": "2026-01-06", "exit_date": "2026-01-10",
         "entry_price": 200.0, "exit_price": 210.0, "qty": 10, "exit_type": "target"},
    ])
    trades = compute_pnl(trades)
    m = performance_metrics(trades, initial_equity=10_000.0)
    assert m.num_trades == 2
    assert m.win_rate_pct == 100.0
    assert m.total_return_pct > 0
    assert m.profit_factor == float("inf")


def test_performance_metrics_empty_raises():
    trades = pd.DataFrame(columns=["symbol", "entry_date", "exit_date", "entry_price",
                                    "exit_price", "qty", "exit_type", "commission", "pnl"])
    with pytest.raises(ValueError):
        performance_metrics(trades, initial_equity=10_000.0)


def test_max_drawdown_is_negative_or_zero():
    trades = _trades([
        {"symbol": "AAPL", "entry_date": "2026-01-01", "exit_date": "2026-01-05",
         "entry_price": 100.0, "exit_price": 90.0, "qty": 10, "exit_type": "stop_loss"},
    ])
    trades = compute_pnl(trades)
    m = performance_metrics(trades, initial_equity=10_000.0)
    assert m.max_drawdown_pct <= 0
