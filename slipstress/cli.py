"""Command-line entry point for SlipStress (Free)."""
from __future__ import annotations
import argparse
import json
import sys

from .io import load_trades, TradeLogError
from .stress import run_stress_test, DEFAULT_STRESSED_EXIT_TYPES

ROW = "{:<22}{:>14}{:>14}"
PRO_INFO = ("SlipStress (Pro) adds a multi-level slippage sweep, an equity-curve chart, "
            "design-vs-test fold comparison, and batch processing: "
            "https://algovigil.gumroad.com/l/slipstress")


def _print_report(result) -> None:
    b, s = result.baseline, result.stressed
    print(f"\nSlipStress -- {result.slip_pct * 100:.2f}% slippage on "
          f"{', '.join(result.stressed_exit_types)} exits\n")
    print(ROW.format("Metric", "Baseline", "Stressed"))
    print("-" * 50)
    print(ROW.format("Trades", b.num_trades, s.num_trades))
    print(ROW.format("Total return %", b.total_return_pct, s.total_return_pct))
    print(ROW.format("CAGR %", b.cagr_pct, s.cagr_pct))
    print(ROW.format("Sharpe", b.sharpe, s.sharpe))
    print(ROW.format("Max drawdown %", b.max_drawdown_pct, s.max_drawdown_pct))
    print(ROW.format("Profit factor", b.profit_factor, s.profit_factor))
    print(ROW.format("Win rate %", b.win_rate_pct, s.win_rate_pct))
    print(ROW.format("Expectancy $", b.expectancy, s.expectancy))
    print(f"\n{PRO_INFO}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="slipstress",
        description="SlipStress (Free) -- haircut your backtest's stop-type exits by a "
                    "slippage percentage and see what survives.")
    parser.add_argument("--trades", required=True, help="Path to a trade-log CSV (see README).")
    parser.add_argument("--slip-pct", type=float, required=True,
                         help="Slippage to apply, as a percent (e.g. 0.28 for 0.28%%).")
    parser.add_argument("--initial-equity", type=float, default=100_000.0)
    parser.add_argument("--stressed-exit-types", default=",".join(DEFAULT_STRESSED_EXIT_TYPES),
                         help="Comma-separated exit_type values to haircut "
                              f"(default: {','.join(DEFAULT_STRESSED_EXIT_TYPES)}).")
    parser.add_argument("--out", default=None, help="Optional path to write the result as JSON.")
    args = parser.parse_args()

    try:
        trades = load_trades(args.trades)
    except TradeLogError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    stressed_exit_types = tuple(t.strip() for t in args.stressed_exit_types.split(",") if t.strip())
    result = run_stress_test(trades, args.initial_equity, args.slip_pct / 100.0, stressed_exit_types)
    _print_report(result)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(result.as_dict(), f, indent=2)
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
