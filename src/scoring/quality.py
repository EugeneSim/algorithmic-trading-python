"""Quality and low-volatility overlay scoring and filtering."""
import pandas as pd
import numpy as np
from typing import Optional

def compute_quality_score(
    df: pd.DataFrame,
    roe_col: str = "ROE",
    earnings_stability_col: Optional[str] = None,
) -> pd.DataFrame:
    """Simple quality score from ROE and optional earnings stability. Higher = better."""
    out = df.copy()
    if roe_col in out.columns:
        out["Quality_ROE"] = out[roe_col].fillna(0)
    else:
        out["Quality_ROE"] = 0
    if earnings_stability_col and earnings_stability_col in out.columns:
        out["Quality_Stability"] = out[earnings_stability_col].fillna(0)
    else:
        out["Quality_Stability"] = 0
    out["Quality Score"] = (out["Quality_ROE"] + out["Quality_Stability"]) / 2
    return out

def quality_filter(
    df: pd.DataFrame,
    min_roe: float = 0.10,
    roe_col: str = "ROE",
) -> pd.DataFrame:
    """Filter to rows with ROE >= min_roe. Pass-through if roe_col missing."""
    if roe_col not in df.columns:
        return df
    return df[df[roe_col].fillna(-1) >= min_roe].copy()

def low_vol_filter(
    df: pd.DataFrame,
    volatility_col: str = "Volatility_12m",
    max_volatility_pct: float = 0.50,
) -> pd.DataFrame:
    """Filter to rows with volatility <= max_volatility_pct."""
    if volatility_col not in df.columns:
        return df
    return df[df[volatility_col].fillna(np.inf) <= max_volatility_pct].copy()
