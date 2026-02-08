"""Returns-based backtest engine for equal-weight, momentum, and value strategies."""
import pandas as pd
import numpy as np
from typing import Optional, List, Callable
from datetime import datetime

def backtest_returns(
    prices: pd.DataFrame,
    rebalance_freq: str = "M",
    initial_capital: float = 100_000,
    ticker_col: str = "Ticker",
    date_col: str = "date",
) -> pd.DataFrame:
    """
    prices: DataFrame with datetime index and columns = tickers (or long format with ticker_col, date_col).
    rebalance_freq: 'M' monthly, 'W' weekly.
    Returns: series of portfolio equity (or period returns).
    """
    if date_col in prices.columns and ticker_col in prices.columns:
        # Pivot to wide: index = date, columns = ticker, values = price
        wide = prices.pivot(index=date_col, columns=ticker_col, values=prices.columns[-1])
        if wide.index.dtype != "datetime64[ns]":
            wide.index = pd.to_datetime(wide.index)
    else:
        wide = prices
    wide = wide.dropna(how="all").ffill()
    rets = wide.pct_change().dropna(how="all")
    if rets.empty:
        return pd.Series(dtype=float)
    rule = "ME" if rebalance_freq.upper() == "M" else "W"
    rb_dates = rets.resample(rule).last().dropna(how="all").index
    n = len(wide.columns)
    w = np.ones(n) / n
    equity = [initial_capital]
    for t in rets.index:
        if t in rb_dates:
            w = np.ones(n) / n
        r = rets.loc[t].values
        r = np.nan_to_num(r, nan=0.0, posinf=0.0, neginf=0.0)
        r = np.clip(r, -1.0, 10.0)
        port_ret = np.dot(w, r)
        port_ret = np.clip(port_ret, -1.0, 2.0)
        equity.append(equity[-1] * (1 + port_ret))
    equity_series = pd.Series(equity[1:], index=rets.index)
    return equity_series

def backtest_summary(
    equity: pd.Series,
    risk_free_rate: float = 0.02,
) -> dict:
    """Compute total return, volatility (ann.), Sharpe, max drawdown, Calmar."""
    if equity.empty or len(equity) < 2:
        return {}
    total_ret = (equity.iloc[-1] / equity.iloc[0]) - 1
    rets = equity.pct_change().dropna()
    vol = rets.std() * np.sqrt(252) if len(rets) > 1 else 0
    rf_daily = risk_free_rate / 252
    sharpe = (rets.mean() - rf_daily) / (rets.std() + 1e-12) * np.sqrt(252) if rets.std() > 0 else 0
    cummax = equity.cummax()
    dd = (equity - cummax) / cummax
    max_dd = dd.min()
    calmar = total_ret / (abs(max_dd) + 1e-12) if max_dd != 0 else 0
    return {
        "total_return": total_ret,
        "volatility_ann": vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd,
        "calmar_ratio": calmar,
    }
