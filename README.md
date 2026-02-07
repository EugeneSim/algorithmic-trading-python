# Algorithmic Trading in Python

This repository contains course materials and code for building algorithmic trading strategies in Python: equal-weight S&P 500, quantitative momentum (HQM), and quantitative value (RV), plus a full set of **expansion modules** for backtesting, multi-factor, sector/quality, and reporting.

## Quick Start

```bash
pip install -r requirements.txt
# Optional: add secrets.py with IEX_CLOUD_API_TOKEN for IEX Cloud
python scripts/run_backtest.py          # Backtest, walk-forward, Monte Carlo
python scripts/run_all_expansions.py     # Multi-factor, sector, weighting, dashboard
python scripts/rebalance.py --value 100000
python scripts/compare_etfs.py --etfs MTUM IWD RPV
```

- **Config:** `config/strategy_config.yaml`  
- **Shared package:** `src/` (data, scoring, portfolio, backtest, walk_forward, monte_carlo, reports)  
- **Factor primer:** `docs/FACTOR_PRIMER.md`  
- **Expansion checklist:** `EXPANSION_TODO.md`

## Course Outline

* Section 1: Algorithmic Trading Fundamentals
  * What is Algorithmic Trading?
  * The Differences Between Real-World Algorithmic Trading and This Course
* Section 2: Course Configuration & API Basics
  * How to Install Python
  * Cloning The Repository & Installing Our Dependencies
  * Jupyter Notebook Basics
  * The Basics of API Requests
* Section 3: Building An Equal-Weight S&P 500 Index Fund
  * Theory & Concepts
  * Importing our Constituents
  * Pulling Data For Our Constituents
  * Calculating Weights
  * Generating Our Output File
  * Additional Project Ideas
* Section 4: Building A Quantitative Momentum Investing Strategy
  * Theory & Concepts
  * Pulling Data For Our Constituents
  * Calculating Weights
  * Generating Our Output File
  * Additional Project Ideas
* Section 5: Building A Quantitative Value Investing Strategy
  * Theory & Concepts
  * Importing our Constituents
  * Pulling Data For Our Constituents
  * Calculating Weights
  * Generating Our Output File
  * Additional Project Ideas
