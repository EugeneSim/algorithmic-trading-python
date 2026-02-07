"""Momentum scoring: HQM and alternative definitions (52-week high, risk-adjusted)."""
import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Optional

TIME_PERIODS = ["One-Year", "Six-Month", "Three-Month", "One-Month"]

def compute_hqm_score(
    df: pd.DataFrame,
    return_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    High-Quality Momentum: percentile of 1y, 6m, 3m, 1m returns; HQM = mean of percentiles.
    df must have columns like 'One-Year Price Return', 'Six-Month Price Return', etc.
    """
    periods = return_columns or [f"{p} Price Return" for p in TIME_PERIODS]
    out = df.copy()
    for col in periods:
        if col not in out.columns:
            continue
        pct_col = col.replace(" Price Return", " Return Percentile")
        out[pct_col] = out[col].rank(pct=True)
    pct_cols = [c for c in out.columns if "Return Percentile" in c]
    if pct_cols:
        out["HQM Score"] = out[pct_cols].mean(axis=1)
    return out

def compute_52w_high_proximity(price: float, week52high: float) -> float:
    """52-week high proximity: price / 52w high. Higher = closer to high (momentum)."""
    if week52high and week52high > 0:
        return price / week52high
    return np.nan

def compute_risk_adjusted_momentum(
    returns: pd.Series,
    volatility: pd.Series,
) -> pd.Series:
    """Risk-adjusted momentum: return / volatility (e.g. 12m return / 12m vol)."""
    out = returns / volatility.replace(0, np.nan)
    return out
