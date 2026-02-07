#!/usr/bin/env python3
"""Run backtest, walk-forward, and Monte Carlo using historical data (yfinance)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np

def fetch_returns(tickers, start="2015-01-01", end=None):
    try:
        import yfinance as yf
    except ImportError:
        print("Install yfinance: pip install yfinance")
        return pd.DataFrame()
    if not tickers:
        tickers = ["SPY", "AAPL", "MSFT"][:3]
    data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False, group_by="ticker")
    if data.empty:
        return pd.DataFrame()
    if len(tickers) == 1:
        rets = data["Close"].pct_change().dropna()
        rets = pd.DataFrame(rets)
        rets.columns = [tickers[0]]
    else:
        rets = pd.DataFrame(index=data.index)
        for t in tickers:
            if (t, "Close") in data.columns:
                rets[t] = data[t]["Close"].pct_change()
        rets = rets.dropna(how="all")
    return rets

def main():
    from src.data.universe import get_ticker_list
    from src.backtest.engine import backtest_returns, backtest_summary
    from src.walk_forward.testing import walk_forward_test
    from src.monte_carlo.bootstrap import bootstrap_sharpe, monte_carlo_simulate

    tickers = get_ticker_list()
    if len(tickers) > 50:
        tickers = tickers[:50]
    if not tickers:
        tickers = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "JPM", "V"]
    print("Fetching historical returns (sample)...")
    rets = fetch_returns(tickers, start="2015-01-01")
    if rets.empty:
        print("No data; using random returns for demo.")
        np.random.seed(42)
        dates = pd.date_range("2015-01-01", periods=252*5, freq="B")
        rets = pd.DataFrame(np.random.randn(len(dates), 10) * 0.01, index=dates)

    # Backtest
    equity = backtest_returns(rets, rebalance_freq="M", initial_capital=100_000)
    summary = backtest_summary(equity)
    print("Backtest summary:", summary)

    # Walk-forward
    wf = walk_forward_test(rets.iloc[:, 0] if rets.shape[1] > 0 else rets, train_months=36, test_months=12, step_months=12)
    print("Walk-forward (first 3 folds):")
    print(wf.head(3).to_string() if not wf.empty else "N/A")

    # Monte Carlo
    monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1).iloc[:, 0]
    mean_s, lo, hi = bootstrap_sharpe(monthly, n_simulations=500, block_size=12)
    print("Bootstrap Sharpe: mean=%.3f, 5%%=%.3f, 95%%=%.3f" % (mean_s, lo, hi))
    paths = monte_carlo_simulate(monthly, n_simulations=100, horizon=24, block_bootstrap=True, block_size=6)
    print("Monte Carlo paths shape:", paths.shape)
    return 0

if __name__ == "__main__":
    sys.exit(main())
