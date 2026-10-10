# SlipStress (Free)

Slippage-stress test your own backtested trades.

Most backtests assume every exit fills at exactly the price your code
computed. In real markets, that's only true for exits priced off what the
market is actually doing right now (end-of-day, a time stop). A **stop-loss
or trailing stop fires at a level your code calculated in advance** — and by
the time an order reaches the book, price has often already moved past it.
That gap is where a backtest's edge quietly evaporates in live trading.

SlipStress takes a trade log you've already produced from your own backtest,
haircuts the exit price on whichever exit types you tag as "computed level"
(stop-loss, trailing stop, etc.), and recomputes performance so you can see
exactly how much of your edge survives.

This isn't a trading strategy and it doesn't generate signals. It's a stress
test for a strategy you already have.

## Install

```bash
git clone https://github.com/mthameed/slipstress.git
cd slipstress
pip install -e .
```

## Quick start

```bash
slipstress-free --trades example_trades.csv --slip-pct 0.28
```

```
SlipStress -- 0.28% slippage on stop_loss, trailing_stop, atr_stop exits

Metric                      Baseline      Stressed
--------------------------------------------------
Trades                            20            20
Total return %                  4.27          3.91
CAGR %                          25.2          22.9
Sharpe                         3.801         3.563
Max drawdown %                 -0.77         -0.83
Profit factor                  3.175         2.786
Win rate %                      50.0          50.0
Expectancy $                  213.67        195.68
```

## Your trade log format

A CSV with one row per closed **long** trade:

| column       | meaning                                                        |
|--------------|-----------------------------------------------------------------|
| symbol       | ticker                                                           |
| entry_date   | entry date/time                                                 |
| exit_date    | exit date/time                                                  |
| entry_price  | fill price at entry                                              |
| exit_price   | fill price at exit (baseline, unstressed)                       |
| qty          | shares (positive)                                                |
| exit_type    | why the trade closed — this is what SlipStress keys off          |
| commission   | optional, defaults to 0                                         |

`exit_type` is the whole point: tag which exits in your backtest fire at a
*computed* level (`stop_loss`, `trailing_stop`, `atr_stop`, ...) versus a
*market-observed* one (`target`, `time_exit`, `eod_exit`, ...). By default,
SlipStress stresses `stop_loss`, `trailing_stop`, and `atr_stop` — override
with `--stressed-exit-types` if your naming differs.

See `example_trades.csv` in this repo for a working sample.

## What it computes

Total return, CAGR, Sharpe, max drawdown, profit factor, win rate, and
expectancy — once on your trades as-is (baseline), once with the slippage
haircut applied (stressed). Same metrics, side by side, so the real cost of
slippage is a number instead of a guess.

## Free vs Pro

The free tier runs one slippage level against one trade log and prints a
console comparison. That's often enough to answer "does this still work
after slippage?" — it's genuinely open source (MIT), not a crippled trial.

**SlipStress (Pro)** — [algovigil.gumroad.com/l/slipstress](https://algovigil.gumroad.com/l/slipstress) — adds:

| | Free | Pro |
|---|---|---|
| Single slippage-level stress test | ✓ | ✓ |
| Baseline vs stressed comparison | ✓ | ✓ |
| Slippage **sweep** (degradation curve across multiple levels) | — | ✓ |
| Equity-curve chart (baseline vs stressed, overlaid) | — | ✓ |
| Design-fold vs test-fold comparison | — | ✓ |
| Batch mode (a whole folder of trade logs in one report) | — | ✓ |
| Excel (.xlsx) report export | — | ✓ |

## Why this exists

Built out of a real, recurring pattern: strategies that looked strong in a
frictionless backtest and lost most or all of their edge once realistic
slippage was applied — repeatedly, across several independent strategies,
before ever going live. This is that same check, generalized to run against
any trade log instead of one specific codebase.

## License

MIT — see [LICENSE.md](LICENSE.md). This isn't a feature-limited demo; the
free tier's code is the whole single-run stress test, with nothing disabled.
