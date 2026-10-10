import pandas as pd
import pytest
from slipstress.stress import apply_slippage, run_stress_test


def _trades(rows):
    df = pd.DataFrame(rows)
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df["exit_date"] = pd.to_datetime(df["exit_date"])
    if "commission" not in df.columns:
        df["commission"] = 0.0
    return df


def test_apply_slippage_only_touches_stressed_exit_types():
    trades = _trades([
        {"symbol": "AAPL", "entry_date": "2026-01-01", "exit_date": "2026-01-05",
         "entry_price": 100.0, "exit_price": 110.0, "qty": 10, "exit_type": "stop_loss"},
        {"symbol": "MSFT", "entry_date": "2026-01-06", "exit_date": "2026-01-10",
         "entry_price": 200.0, "exit_price": 210.0, "qty": 10, "exit_type": "time_exit"},
    ])
    out = apply_slippage(trades, slip_pct=0.10, stressed_exit_types=("stop_loss",))
    assert out.loc[0, "exit_price"] == pytest.approx(110.0 * 0.90)
    assert out.loc[1, "exit_price"] == pytest.approx(210.0)  # untouched


def test_zero_slippage_matches_baseline_exactly():
    trades = _trades([
        {"symbol": "AAPL", "entry_date": "2026-01-01", "exit_date": "2026-01-05",
         "entry_price": 100.0, "exit_price": 90.0, "qty": 10, "exit_type": "stop_loss"},
        {"symbol": "MSFT", "entry_date": "2026-01-06", "exit_date": "2026-01-20",
         "entry_price": 200.0, "exit_price": 215.0, "qty": 10, "exit_type": "trailing_stop"},
    ])
    result = run_stress_test(trades, initial_equity=10_000.0, slip_pct=0.0)
    assert result.baseline.as_dict() == result.stressed.as_dict()


def test_positive_slippage_degrades_stressed_metrics():
    trades = _trades([
        {"symbol": "AAPL", "entry_date": "2026-01-01", "exit_date": "2026-01-05",
         "entry_price": 100.0, "exit_price": 110.0, "qty": 10, "exit_type": "stop_loss"},
        {"symbol": "MSFT", "entry_date": "2026-01-06", "exit_date": "2026-01-20",
         "entry_price": 200.0, "exit_price": 230.0, "qty": 10, "exit_type": "trailing_stop"},
    ])
    result = run_stress_test(trades, initial_equity=10_000.0, slip_pct=0.28 / 100)
    assert result.stressed.total_return_pct < result.baseline.total_return_pct


def test_untagged_exit_types_are_never_stressed():
    trades = _trades([
        {"symbol": "AAPL", "entry_date": "2026-01-01", "exit_date": "2026-01-05",
         "entry_price": 100.0, "exit_price": 110.0, "qty": 10, "exit_type": "eod_exit"},
    ])
    result = run_stress_test(trades, initial_equity=10_000.0, slip_pct=0.50)
    assert result.baseline.total_return_pct == result.stressed.total_return_pct
