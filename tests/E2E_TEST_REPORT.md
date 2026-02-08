# End-to-End Test Report

## Summary

| Category | Status | Details |
|----------|--------|---------|
| **Old notebook logic (001, 002, 003)** | PASS | 6 tests: equal-weight calc, Excel output, HQM/RV percentiles, top-50 selection, imports |
| **New expansion (src/ + scripts)** | PASS | 20 tests: config, data, scoring, portfolio, backtest, walk-forward, Monte Carlo, reports, all 4 scripts |
| **Scripts exit codes** | PASS | rebalance.py, compare_etfs.py, run_backtest.py, run_all_expansions.py all return 0 |
| **Output accuracy** | VERIFIED | See assertions below |

**Total: 26/26 pytest tests passed.**

---

## What Was Tested

### Old Work (No Breaking Change)

1. **001 Equal-Weight S&P 500**
   - `position_size = portfolio_size / n`; `shares = floor(position_size / price)`.
   - Verified: 5 stocks, $100k → position_size $20k; first stock $100 → 200 shares.
   - Excel: written with columns Ticker, Price, Market Capitalization, Number Of Shares to Buy; read back and asserted.

2. **002 Quantitative Momentum**
   - HQM = mean of 1y, 6m, 3m, 1m return percentiles; sort descending; top 50.
   - Verified: percentile calculation and that highest return stock gets highest HQM; top-50 selection monotonic.

3. **003 Quantitative Value**
   - RV = mean of PE, PB, EV/EBITDA percentiles (lower raw = cheaper); sort ascending; top 50.
   - Verified: lowest P/E stock (C) has lowest RV and is first after sort.

4. **Dependencies**
   - numpy, pandas, requests, xlsxwriter, math, scipy.stats all import successfully.

### New Work (Expansion)

- **Config:** YAML/JSON load; universe, data, strategies keys present.
- **Data:** Universe load from fixture CSV; survivorship-aware loader; get_ticker_list().
- **Scoring:** HQM score, RV score, quality filter/score, 52w high proximity, risk-adjusted momentum, alternative value metrics (earnings_yield, fcf_yield, dividend_yield).
- **Portfolio:** weights_equal, weights_risk_parity, weights_conviction, weights_min_variance, weights_max_sharpe, apply_weight_bounds; sector_neutral, sector_tilt.
- **Backtest:** backtest_returns(), backtest_summary() with synthetic returns; total_return, sharpe_ratio, max_drawdown in summary.
- **Walk-forward:** walk_forward_test() returns DataFrame with train/test bounds and test metrics.
- **Monte Carlo:** monte_carlo_simulate() shape; bootstrap_sharpe() returns (mean, 5%, 95%).
- **Reports:** correlation_report() avg_correlation in [-1,1], hhi; build_dashboard_html() content and file write.
- **Scripts:** rebalance.py, compare_etfs.py, run_backtest.py, run_all_expansions.py each run with exit code 0; run_all_expansions produces reports/dashboard.html.

---

## Output Accuracy Checks

- **001 shares:** `floor(20000/100) = 200` ✓  
- **001 Excel:** Columns and values round-trip (66, 26 shares) ✓  
- **002 HQM:** Best momentum stock has highest HQM ✓  
- **003 RV:** Cheapest stock (lowest P/E) has lowest RV and is first ✓  
- **Quality filter:** ROE ≥ 10% keeps 2 of 3 rows ✓  
- **52w high proximity:** 90/100 = 0.9 ✓  
- **Alternative value:** earnings_yield = 4/100 = 0.04 ✓  
- **Weights:** Sum to 1.0 for equal, risk parity, conviction ✓  
- **Backtest summary:** Keys present; total_return/sharpe/max_drawdown finite or handled ✓  

---

## How to Run

```bash
# Full test suite
python -m pytest tests/ -v --tb=short

# E2E runner (pytest + scripts)
python tests/run_e2e_tests.py
```

**Note:** Executing the original notebooks (001–003) via nbconvert requires `sp_500_stocks.csv` and `secrets.py` (or IEX token) in the notebook directory; the fixture CSV and optional stub are used by `run_e2e_tests.py` when nbconvert is installed. Executing the 004 notebook requires a Jupyter kernel (e.g. `python3`) to be installed.
