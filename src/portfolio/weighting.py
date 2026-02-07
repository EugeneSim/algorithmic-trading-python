"""Portfolio weighting: equal, risk parity, volatility-scaled, conviction, min-var, max-Sharpe."""
import pandas as pd
import numpy as np
from typing import Optional

def weights_equal(n: int) -> np.ndarray:
    """Equal weight."""
    return np.ones(n) / n

def weights_risk_parity(volatilities: np.ndarray) -> np.ndarray:
    """Inverse volatility (risk parity). vol can be 1d array of per-asset vol."""
    vol = np.asarray(volatilities, dtype=float)
    vol = np.where(vol <= 0, np.nan, vol)
    inv = 1.0 / vol
    inv = np.nan_to_num(inv, nan=0.0)
    w = inv / inv.sum()
    return w

def weights_volatility_scaled(volatilities: np.ndarray) -> np.ndarray:
    """Same as risk parity for 1/vol scaling."""
    return weights_risk_parity(volatilities)

def weights_conviction(scores: np.ndarray, power: float = 1.0) -> np.ndarray:
    """Weight proportional to score^power; then normalize."""
    s = np.asarray(scores, dtype=float)
    s = np.where(np.isnan(s), 0, np.maximum(s, 0))
    w = np.power(s + 1e-8, power)
    return w / w.sum()

def weights_min_variance(cov: np.ndarray) -> np.ndarray:
    """Minimum variance portfolio (no expected return; min w'Cw s.t. sum(w)=1, w>=0)."""
    n = cov.shape[0]
    ones = np.ones(n)
    try:
        inv = np.linalg.inv(cov + np.eye(n) * 1e-8)
        w = inv @ ones
        w = w / w.sum()
        w = np.clip(w, 0, 1)
        w = w / w.sum()
        return w
    except Exception:
        return np.ones(n) / n

def weights_max_sharpe(
    mean_returns: np.ndarray,
    cov: np.ndarray,
    risk_free: float = 0.0,
) -> np.ndarray:
    """Max Sharpe (tangency) weights: inv(Cov) @ (mu - rf); then normalize and clip."""
    n = cov.shape[0]
    mu = np.asarray(mean_returns).ravel()[:n]
    mu = mu - risk_free
    try:
        inv = np.linalg.inv(cov + np.eye(n) * 1e-8)
        w = inv @ mu
        w = np.clip(w, 0, np.inf)
        if w.sum() <= 0:
            return np.ones(n) / n
        w = w / w.sum()
        return w
    except Exception:
        return np.ones(n) / n

def apply_weight_bounds(w: np.ndarray, min_w: float = 0.0, max_w: float = 1.0) -> np.ndarray:
    """Clip and renormalize weights to [min_w, max_w]."""
    w = np.clip(w, min_w, max_w)
    return w / w.sum()
