"""Walk-forward / out-of-sample testing."""
import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
from datetime import datetime

def walk_forward_test(
    returns: pd.DataFrame,
    train_months: int = 60,
    test_months: int = 12,
    step_months: int = 12,
) -> pd.DataFrame:
    """
    returns: DataFrame with datetime index; columns = assets (or single column = strategy return).
    Rolling: train on train_months, evaluate on next test_months; step by step_months.
    Returns DataFrame with columns: train_start, train_end, test_start, test_end, test_return, test_vol, test_sharpe.
    """
    if returns.empty or len(returns) < train_months + test_months:
        return pd.DataFrame()
    if isinstance(returns, pd.Series):
        returns = pd.DataFrame(returns)
    if returns.index.dtype != "datetime64[ns]":
        returns.index = pd.to_datetime(returns.index)
    monthly = returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    rows = []
    i = 0
    while i + train_months + test_months <= len(monthly):
        train = monthly.iloc[i : i + train_months]
        test = monthly.iloc[i + train_months : i + train_months + test_months]
        train_start = train.index[0]
        train_end = train.index[-1]
        test_start = test.index[0]
        test_end = test.index[-1]
        test_ret = (1 + test).prod() - 1
        if isinstance(test_ret, pd.Series):
            test_ret = test_ret.iloc[0] if len(test_ret.shape) > 0 else 0
        test_vol = test.std()
        if isinstance(test_vol, pd.Series):
            test_vol = test_vol.iloc[0]
        test_vol_ann = test_vol * np.sqrt(12) if test_vol and not np.isnan(test_vol) else 0
        test_sharpe = (test_ret / (test_vol + 1e-12)) * np.sqrt(12) if test_vol else 0
        rows.append({
            "train_start": train_start,
            "train_end": train_end,
            "test_start": test_start,
            "test_end": test_end,
            "test_return": test_ret,
            "test_vol_ann": test_vol_ann,
            "test_sharpe": test_sharpe,
        })
        i += step_months
    return pd.DataFrame(rows)
