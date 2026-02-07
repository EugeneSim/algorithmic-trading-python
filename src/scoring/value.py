"""Value scoring: RV (composite) and alternative metrics (FCF yield, E/P, dividend yield)."""
import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Optional, Dict, Any

VALUE_METRICS = ["Price-to-Earnings Ratio", "Price-to-Book Ratio", "Price-to-Sales Ratio", "EV/EBITDA", "EV/GP"]

def compute_rv_score(df: pd.DataFrame, metric_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Robust Value: for each metric lower is better; percentile (low = cheap); RV = mean of percentiles.
    """
    metrics = metric_columns or VALUE_METRICS
    out = df.copy()
    for col in metrics:
        if col not in out.columns:
            continue
        pct_col = col + " Percentile"
        if "P/E" in col or "PE" in col:
            pct_col = "PE Percentile"
        elif "P/B" in col or "PB" in col or "Price-to-Book" in col:
            pct_col = "PB Percentile"
        elif "P/S" in col or "PS" in col or "Price-to-Sales" in col:
            pct_col = "PS Percentile"
        elif "EV/EBITDA" in col:
            pct_col = "EV/EBITDA Percentile"
        elif "EV/GP" in col:
            pct_col = "EV/GP Percentile"
        # Lower raw value = cheaper = higher percentile for "cheap"
        out[pct_col] = out[col].rank(pct=True)
    pct_cols = [c for c in out.columns if "Percentile" in c and "RV" not in c]
    if pct_cols:
        out["RV Score"] = out[pct_cols].mean(axis=1)
    return out

def compute_alternative_value_metrics(
    pe_ratio: float,
    earnings_per_share: float,
    price: float,
    free_cash_flow: Optional[float] = None,
    dividend_per_share: Optional[float] = None,
) -> Dict[str, Any]:
    """Compute FCF yield, earnings yield (E/P), dividend yield when data available."""
    result = {}
    if price and price > 0:
        if earnings_per_share is not None and earnings_per_share > 0:
            result["earnings_yield"] = earnings_per_share / price
        if free_cash_flow is not None and free_cash_flow > 0:
            # FCF yield typically FCF per share / price or FCF / market cap
            result["fcf_yield"] = free_cash_flow / price
        if dividend_per_share is not None and dividend_per_share >= 0:
            result["dividend_yield"] = dividend_per_share / price
    return result
