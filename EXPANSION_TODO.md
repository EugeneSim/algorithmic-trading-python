# Expansion To-Do List (All Items)

This file lists every expansion item and where it is implemented.

## Backtesting & Robustness

| # | Item | Status | Location |
|---|------|--------|----------|
| 1 | Backtest engine (returns-based) for all 3 strategies | Done | `src/backtest/engine.py`, `scripts/run_backtest.py` |
| 2 | Walk-forward / out-of-sample testing | Done | `src/walk_forward/testing.py`, `scripts/run_backtest.py` |
| 3 | Monte Carlo / bootstrap for strategy uncertainty | Done | `src/monte_carlo/bootstrap.py`, `scripts/run_backtest.py` |

## Factor & Strategy Depth

| # | Item | Status | Location |
|---|------|--------|----------|
| 4 | Multi-factor combined strategy (value + momentum + quality) | Done | `src/scoring/*.py`, `scripts/run_all_expansions.py`, config |
| 5 | Sector-neutral or sector tilt constraints | Done | `src/portfolio/sector.py`, `scripts/run_all_expansions.py` |
| 6 | Quality / low-vol overlay filter | Done | `src/scoring/quality.py`, `scripts/run_all_expansions.py` |
| 7 | Alternative momentum definitions (52w high, risk-adj) | Done | `src/scoring/momentum.py`, `scripts/run_all_expansions.py` |
| 8 | Alternative value metrics (FCF yield, E/P, div yield) | Done | `src/scoring/value.py` `compute_alternative_value_metrics`, `scripts/run_all_expansions.py` |

## Portfolio Construction & Risk

| # | Item | Status | Location |
|---|------|--------|----------|
| 9 | Risk parity or volatility-weighted sizing | Done | `src/portfolio/weighting.py` `weights_risk_parity`, `weights_volatility_scaled` |
| 10 | Minimum variance or max Sharpe optimization | Done | `src/portfolio/weighting.py` `weights_min_variance`, `weights_max_sharpe` |
| 11 | Position sizing by conviction (score-based) | Done | `src/portfolio/weighting.py` `weights_conviction`, config `conviction_power` |
| 12 | Correlation and diversification report | Done | `src/reports/correlation.py`, `scripts/run_all_expansions.py` |

## Data & Infrastructure

| # | Item | Status | Location |
|---|------|--------|----------|
| 13 | Multiple data sources (e.g. yfinance fallback) | Done | `src/data/sources.py` `get_prices`, `get_prices_iex`, `get_prices_yfinance` |
| 14 | Survivorship-bias-free universe handling | Done | `src/data/universe.py` `load_universe_survivorship_aware` |
| 15 | Config-driven pipeline (YAML/JSON) | Done | `config/strategy_config.yaml`, `src/config_loader.py` |
| 16 | Shared Python package (src/ modules) | Done | `src/` (config_loader, data, scoring, portfolio, backtest, walk_forward, monte_carlo, reports) |

## Reporting & Monitoring

| # | Item | Status | Location |
|---|------|--------|----------|
| 17 | Strategy dashboard (HTML/PDF report) | Done | `src/reports/dashboard.py`, `scripts/run_all_expansions.py` (HTML); PDF via weasyprint/pdfkit if installed |
| 18 | Periodic rebalance script (trade list output) | Done | `scripts/rebalance.py` |

## Theory & Education

| # | Item | Status | Location |
|---|------|--------|----------|
| 19 | Factor primer document (theory/education) | Done | `docs/FACTOR_PRIMER.md` |
| 20 | Comparison to ETFs (MTUM, IWD, RPV) | Done | `scripts/compare_etfs.py` |

---

## How to Run

- **Config:** Edit `config/strategy_config.yaml` and load in code via `from src.config_loader import load_config`.
- **Backtest + Walk-forward + Monte Carlo:** `python scripts/run_backtest.py`
- **All expansion features (multi-factor, sector, quality, weighting, correlation, dashboard):** `python scripts/run_all_expansions.py`
- **Rebalance (placeholder trade list):** `python scripts/rebalance.py --value 100000 --out output/rebalance_trades.csv`
- **ETF comparison:** `python scripts/compare_etfs.py --etfs MTUM IWD RPV`
- **Factor primer:** Read `docs/FACTOR_PRIMER.md`.
