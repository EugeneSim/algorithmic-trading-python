"""Sector-neutral and sector-tilt constraints."""
import pandas as pd
import numpy as np
from typing import Dict, Optional, List

def sector_weights_from_benchmark(
    benchmark_weights: Dict[str, float],
) -> Dict[str, float]:
    """Return benchmark sector weights (e.g. from config or S&P 500 sector breakdown)."""
    return dict(benchmark_weights)

def apply_sector_neutral(
    df: pd.DataFrame,
    sector_col: str = "Sector",
    target_sector_weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """
    Within each sector, equal-weight names so that total sector weight matches target.
    df must have Sector column. target_sector_weights: sector -> weight (e.g. 0.25 for 25%).
    """
    if sector_col not in df.columns:
        return df
    out = df.copy()
    out["_count"] = 1
    sector_counts = out.groupby(sector_col).size()
    total = len(out)
    if target_sector_weights:
        out["Weight"] = out[sector_col].map(
            lambda s: (target_sector_weights.get(s, 1 / len(sector_counts)) / max(1, sector_counts.get(s, 1)))
        )
    else:
        out["Weight"] = out[sector_col].map(
            lambda s: 1.0 / max(total, sector_counts.get(s, 1))
        )
    out["Weight"] = out["Weight"] / out["Weight"].sum()
    return out

def apply_sector_tilt(
    df: pd.DataFrame,
    sector_col: str = "Sector",
    tilt: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """
    tilt: e.g. {"Technology": 1.2, "Energy": 0.8} multiplies sector weights.
    """
    if not tilt or sector_col not in df.columns:
        return df
    out = df.copy()
    if "Weight" not in out.columns:
        out["Weight"] = 1.0 / len(out)
    out["Weight"] = out["Weight"] * out[sector_col].map(lambda s: tilt.get(s, 1.0))
    out["Weight"] = out["Weight"] / out["Weight"].sum()
    return out
