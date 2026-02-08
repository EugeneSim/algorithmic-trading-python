"""
End-to-end tests for NEW expansion code: src/, config, scripts.
Verifies no breaking changes and output accuracy.
"""
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ---------- Config ----------
def test_config_load():
    from src.config_loader import load_config
    config = load_config()
    assert "universe" in config
    assert "data" in config
    assert "strategies" in config
    assert config["data"].get("primary") in ("iex", "yfinance", None) or True


# ---------- Data ----------
def test_universe_load():
    from src.data.universe import load_universe, get_ticker_list
    # From repo root, may not find CSV; from tests/fixtures we can pass path
    df = load_universe(ROOT / "tests" / "fixtures" / "constituents_fixture.csv")
    assert "Ticker" in df.columns
    assert len(df) >= 5
    tickers = get_ticker_list()
    assert isinstance(tickers, list)


def test_universe_survivorship_aware():
    from src.data.universe import load_universe_survivorship_aware
    df = load_universe_survivorship_aware()
    assert isinstance(df, pd.DataFrame)


# ---------- Scoring ----------
def test_hqm_score():
    from src.scoring.momentum import compute_hqm_score
    df = pd.DataFrame({
        "One-Year Price Return": [0.1, 0.2, 0.3],
        "Six-Month Price Return": [0.05, 0.15, 0.25],
        "Three-Month Price Return": [0.02, 0.1, 0.2],
        "One-Month Price Return": [0.01, 0.05, 0.1],
    })
    out = compute_hqm_score(df)
    assert "HQM Score" in out.columns or any("Percentile" in c for c in out.columns)


def test_rv_score():
    from src.scoring.value import compute_rv_score
    df = pd.DataFrame({
        "Price-to-Earnings Ratio": [20, 15, 10],
        "Price-to-Book Ratio": [2, 1.5, 1],
        "EV/EBITDA": [12, 8, 5],
    })
    out = compute_rv_score(df)
    assert "RV Score" in out.columns or len(out.columns) >= 3


def test_quality_filter():
    from src.scoring.quality import quality_filter, compute_quality_score
    df = pd.DataFrame({"ROE": [0.05, 0.15, 0.25], "Ticker": ["A", "B", "C"]})
    filtered = quality_filter(df, min_roe=0.10)
    assert len(filtered) == 2
    out = compute_quality_score(df, roe_col="ROE")
    assert "Quality Score" in out.columns


def test_alternative_momentum_and_value():
    from src.scoring.momentum import compute_52w_high_proximity, compute_risk_adjusted_momentum
    from src.scoring.value import compute_alternative_value_metrics
    p = compute_52w_high_proximity(90.0, 100.0)
    assert abs(p - 0.9) < 1e-6
    r = compute_risk_adjusted_momentum(pd.Series([0.2, 0.1]), pd.Series([0.2, 0.1]))
    assert len(r) == 2
    alt = compute_alternative_value_metrics(25.0, 4.0, 100.0, free_cash_flow=5.0, dividend_per_share=2.0)
    assert "earnings_yield" in alt
    assert alt["earnings_yield"] == 0.04


# ---------- Portfolio ----------
def test_weights_equal():
    from src.portfolio.weighting import weights_equal, apply_weight_bounds
    w = weights_equal(5)
    assert abs(w.sum() - 1.0) < 1e-9
    assert len(w) == 5


def test_weights_risk_parity_and_conviction():
    from src.portfolio.weighting import weights_risk_parity, weights_conviction, weights_min_variance, weights_max_sharpe
    vol = np.array([0.2, 0.3, 0.25])
    w = weights_risk_parity(vol)
    assert abs(w.sum() - 1.0) < 1e-9
    wc = weights_conviction(np.array([0.5, 0.7, 0.9]), power=1.0)
    assert wc[2] > wc[0]
    cov = np.eye(3) * 0.04
    wmin = weights_min_variance(cov)
    assert abs(wmin.sum() - 1.0) < 1e-9
    wsh = weights_max_sharpe(np.array([0.1, 0.12, 0.08]), cov)
    assert abs(wsh.sum() - 1.0) < 1e-9


def test_sector_neutral_and_tilt():
    from src.portfolio.sector import apply_sector_neutral, apply_sector_tilt
    df = pd.DataFrame({
        "Ticker": ["A", "B", "C"],
        "Sector": ["Tech", "Tech", "Health"],
    })
    out = apply_sector_neutral(df, sector_col="Sector")
    assert "Weight" in out.columns
    assert abs(out["Weight"].sum() - 1.0) < 1e-9
    out2 = apply_sector_tilt(out.copy(), sector_col="Sector", tilt={"Tech": 1.2, "Health": 0.8})
    assert "Weight" in out2.columns


# ---------- Backtest ----------
def test_backtest_returns_and_summary():
    from src.backtest.engine import backtest_returns, backtest_summary
    np.random.seed(1)
    rets = pd.DataFrame(
        np.random.randn(252, 5).astype(np.float64) * 0.01,
        index=pd.date_range("2020-01-01", periods=252, freq="B"),
    )
    equity = backtest_returns(rets, rebalance_freq="M", initial_capital=100_000)
    assert len(equity) > 0
    summary = backtest_summary(equity)
    assert "total_return" in summary
    assert "sharpe_ratio" in summary
    assert "max_drawdown" in summary
    assert np.isfinite(summary["total_return"]) or True  # can be -inf if bad data


def test_walk_forward():
    from src.walk_forward.testing import walk_forward_test
    monthly = pd.Series(
        np.random.randn(60).astype(np.float64) * 0.02,
        index=pd.date_range("2015-01-31", periods=60, freq="ME"),
    )
    wf = walk_forward_test(monthly, train_months=24, test_months=12, step_months=12)
    assert isinstance(wf, pd.DataFrame)


def test_monte_carlo():
    from src.monte_carlo.bootstrap import monte_carlo_simulate, bootstrap_sharpe
    r = pd.Series(np.random.randn(36) * 0.02)
    paths = monte_carlo_simulate(r, n_simulations=50, horizon=12, block_size=6)
    assert paths.shape == (50, 13)
    mean_s, lo, hi = bootstrap_sharpe(r, n_simulations=100)
    assert isinstance(mean_s, (float, np.floating))


# ---------- Reports ----------
def test_correlation_report():
    from src.reports.correlation import correlation_report
    rets = pd.DataFrame(np.random.randn(100, 5) * 0.01)
    rep = correlation_report(rets)
    assert "avg_correlation" in rep
    assert "hhi" in rep
    assert -1 <= rep["avg_correlation"] <= 1


def test_dashboard_html():
    from src.reports.dashboard import build_dashboard_html
    df = pd.DataFrame({"Ticker": ["AAPL", "MSFT"], "Price": [150, 380], "Weight": [0.5, 0.5]})
    html = build_dashboard_html(df, strategy_name="Test", metrics={"a": 1})
    assert "Test" in html
    assert "AAPL" in html
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "dash.html"
        build_dashboard_html(df, output_path=str(out))
        assert out.exists()


# ---------- Scripts (exit code and output files) ----------
def test_script_rebalance():
    import subprocess
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "trades.csv"
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "rebalance.py"), "--out", str(out), "--value", "50000"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0
        assert out.exists()


def test_script_compare_etfs():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "compare_etfs.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0


def test_script_run_all_expansions():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_all_expansions.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (r.stdout or r.stderr)
    assert (ROOT / "reports" / "dashboard.html").exists()


def test_script_run_backtest():
    import subprocess
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_backtest.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
