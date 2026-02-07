# Pull Request: Repository Expansion + E2E Testing + Documentation

## Title
**feat: Expansion modules, config-driven pipeline, E2E tests, and documentation**

## Description

This PR extends the algorithmic-trading-python repository with **20 expansion features** (backtest, walk-forward, Monte Carlo, multi-factor, sector/quality, alternative momentum/value, risk parity, min-var, max-Sharpe, conviction sizing, correlation report, multi-source data, survivorship awareness, config pipeline, shared package, dashboard, rebalance script, factor primer, ETF comparison), adds **comprehensive E2E tests** for both original notebooks and new code, and includes **documentation** for running and reviewing everything.

### Summary of changes

| Area | Changes |
|------|--------|
| **Config** | `config/strategy_config.yaml` – single source for universe, data, strategies, portfolio, backtest, output |
| **Shared package** | `src/` – config_loader, data (sources, universe), scoring (momentum, value, quality), portfolio (weighting, sector), backtest, walk_forward, monte_carlo, reports (dashboard, correlation) |
| **Scripts** | `scripts/run_backtest.py`, `run_all_expansions.py`, `rebalance.py`, `compare_etfs.py` |
| **Notebook** | `finished_files/004_expansion_all_features.ipynb` – runs expansion features from config + src |
| **Tests** | `tests/` – fixtures, `test_old_notebooks_logic.py` (001/002/003), `test_new_expansion.py` (src + scripts), `run_e2e_tests.py`, `E2E_TEST_REPORT.md` |
| **Docs** | `docs/FACTOR_PRIMER.md` (factor investing primer), `EXPANSION_TODO.md` (checklist), updated `README.md` |
| **Dependencies** | `requirements.txt` – added PyYAML, yfinance, openpyxl |

### Breaking changes

- **None.** Original notebooks (001, 002, 003) and starter files are unchanged. All new code lives under `config/`, `src/`, `scripts/`, `tests/`, `docs/`, and one new notebook (004).

### How to review

1. **Run tests**
   ```bash
   pip install -r requirements.txt
   python -m pytest tests/ -v --tb=short
   python tests/run_e2e_tests.py
   ```
2. **Run scripts**
   ```bash
   python scripts/run_backtest.py
   python scripts/run_all_expansions.py
   python scripts/rebalance.py --out output/rebalance_trades.csv
   python scripts/compare_etfs.py
   ```
3. **Read docs**
   - `README.md` – quick start and expansion overview
   - `docs/FACTOR_PRIMER.md` – value, momentum, quality theory
   - `EXPANSION_TODO.md` – list of 20 expansion items and locations
   - `tests/E2E_TEST_REPORT.md` – what was tested and output checks

### Checklist

- [x] New code under `src/`, `config/`, `scripts/`, `tests/`, `docs/`
- [x] Original notebooks and logic unchanged; E2E tests verify 001/002/003 behavior
- [x] All 26 pytest tests pass; scripts run with exit 0
- [x] Documentation added (README, factor primer, expansion checklist, test report)
- [x] `.gitignore` updated (output/, reports/, .pytest_cache/)

---

## Branch

- **Branch name:** `feature/expansion-e2e-docs`
- **Base:** `master`

## Related

- Expands on the course outline in README (Sections 3–5) with production-style tooling and tests.
- No issues linked; can be linked to a tracking issue if one exists.
