"""Monte Carlo and block bootstrap for strategy uncertainty."""
import pandas as pd
import numpy as np
from typing import Optional, Tuple

def monte_carlo_simulate(
    returns: pd.Series,
    n_simulations: int = 1000,
    horizon: Optional[int] = None,
    block_bootstrap: bool = True,
    block_size: int = 12,
) -> np.ndarray:
    """
    Simulate future paths: block bootstrap of returns, then compound.
    returns: period returns (e.g. monthly).
    horizon: number of periods to simulate (default = len(returns)).
    Returns: (n_simulations, horizon) array of cumulative wealth paths (starting 1.0).
    """
    r = np.asarray(returns.dropna())
    if len(r) < block_size:
        block_size = max(1, len(r) // 2)
    T = horizon or len(r)
    paths = np.zeros((n_simulations, T + 1))
    paths[:, 0] = 1.0
    for s in range(n_simulations):
        if block_bootstrap:
            n_blocks = (T // block_size) + 1
            blocks = []
            for _ in range(n_blocks):
                start = np.random.randint(0, max(1, len(r) - block_size + 1))
                blocks.extend(r[start : start + block_size].tolist())
            sim_rets = np.array(blocks[:T])
        else:
            sim_rets = np.random.choice(r, size=T, replace=True)
        for t in range(T):
            paths[s, t + 1] = paths[s, t] * (1 + sim_rets[t])
    return paths

def bootstrap_sharpe(
    returns: pd.Series,
    n_simulations: int = 1000,
    block_size: int = 12,
    ann_factor: float = 12,
) -> Tuple[float, float, float]:
    """
    Bootstrap distribution of annualized Sharpe ratio.
    Returns: (mean_sharpe, lower_5pct, upper_95pct).
    """
    r = np.asarray(returns.dropna())
    if len(r) < 2:
        return 0.0, 0.0, 0.0
    sharpes = []
    for _ in range(n_simulations):
        n_blocks = (len(r) // block_size) + 1
        blocks = []
        for _ in range(n_blocks):
            start = np.random.randint(0, max(1, len(r) - block_size + 1))
            blocks.extend(r[start : start + block_size].tolist())
        boot = np.array(blocks[: len(r)])
        mean_r = boot.mean()
        std_r = boot.std()
        if std_r > 0:
            sharpes.append(mean_r / std_r * np.sqrt(ann_factor))
    sharpes = np.array(sharpes)
    return float(sharpes.mean()), float(np.percentile(sharpes, 5)), float(np.percentile(sharpes, 95))
