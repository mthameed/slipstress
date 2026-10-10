"""Load and validate a trade log from CSV.

SlipStress doesn't generate trades -- it stress-tests trades YOU already
produced from your own backtest. This is the only input format it knows
about: one row per closed long trade.
"""
from __future__ import annotations
import pandas as pd

REQUIRED_COLUMNS = [
    "symbol", "entry_date", "exit_date", "entry_price", "exit_price",
    "qty", "exit_type",
]


class TradeLogError(ValueError):
    pass


def load_trades(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise TradeLogError(
            f"Trade log is missing required column(s): {', '.join(missing)}. "
            f"Required columns: {', '.join(REQUIRED_COLUMNS)} "
            "(optional: commission). See the example trade log in this repo.")

    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df["exit_date"] = pd.to_datetime(df["exit_date"])
    if "commission" not in df.columns:
        df["commission"] = 0.0

    if (df["qty"] <= 0).any():
        raise TradeLogError("qty must be positive for every trade (long positions only).")
    if (df["exit_date"] < df["entry_date"]).any():
        raise TradeLogError("exit_date is before entry_date for at least one trade.")

    return df.sort_values("exit_date").reset_index(drop=True)
