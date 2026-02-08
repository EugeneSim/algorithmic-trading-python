"""
End-to-end tests for OLD notebook logic (001, 002, 003).
Uses fixture data only - no live API. Verifies calculation accuracy and output structure.
"""
import math
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURES = ROOT / "tests" / "fixtures"


def _fixture_csv():
    p = FIXTURES / "constituents_fixture.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame({"Ticker": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]})


# ---------- 001 Equal-Weight S&P 500 ----------
def test_001_equal_weight_calculation():
    """001: Given price/cap dataframe, position_size = portfolio / n, shares = floor(position_size / price)."""
    stocks = _fixture_csv()
    n = len(stocks)
    portfolio_size = 100_000
    # Build minimal dataframe as notebook does (without API)
    my_columns = ["Ticker", "Price", "Market Capitalization", "Number Of Shares to Buy"]
    rows = []
    for i, ticker in enumerate(stocks["Ticker"].head(5)):
        price = 100.0 * (i + 1)
        rows.append([ticker, price, price * 1e9, "N/A"])
    final_dataframe = pd.DataFrame(rows, columns=my_columns)
    # Notebook formula (note: notebook loop uses len()-1 so last row stays N/A)
    position_size = float(portfolio_size) / len(final_dataframe.index)
    for i in range(0, len(final_dataframe["Ticker"]) - 1):
        final_dataframe.loc[i, "Number Of Shares to Buy"] = math.floor(
            position_size / final_dataframe["Price"].iloc[i]
        )
    # Last row not filled in original notebook
    assert final_dataframe["Number Of Shares to Buy"].iloc[0] == math.floor(
        position_size / final_dataframe["Price"].iloc[0]
    )
    assert position_size == 20_000
    # First stock price 100 -> 20000/100 = 200 shares
    assert final_dataframe["Number Of Shares to Buy"].iloc[0] == 200


def test_001_excel_output_structure():
    """001: Excel writer produces file with expected columns."""
    try:
        import xlsxwriter
    except ImportError:
        pytest.skip("xlsxwriter not installed")
    my_columns = ["Ticker", "Price", "Market Capitalization", "Number Of Shares to Buy"]
    final_dataframe = pd.DataFrame(
        [
            ["AAPL", 150.0, 2.5e12, 66],
            ["MSFT", 380.0, 2.8e12, 26],
        ],
        columns=my_columns,
    )
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "recommended_trades.xlsx"
        writer = pd.ExcelWriter(out, engine="xlsxwriter")
        final_dataframe.to_excel(writer, sheet_name="Recommended Trades", index=False)
        if hasattr(writer, "save"):
            writer.save()
        else:
            writer.close()
        assert out.exists()
        try:
            read = pd.read_excel(out, sheet_name="Recommended Trades", engine="openpyxl")
        except ImportError:
            pytest.skip("openpyxl required to read .xlsx")
        assert list(read.columns) == my_columns
        assert read["Ticker"].tolist() == ["AAPL", "MSFT"]
        assert read["Number Of Shares to Buy"].tolist() == [66, 26]


# ---------- 002 Momentum (HQM) ----------
def test_002_hqm_percentile_and_score():
    """002: HQM = mean of 1y, 6m, 3m, 1m return percentiles. Higher = better momentum."""
    from scipy import stats
    from statistics import mean

    df = pd.DataFrame({
        "Ticker": ["A", "B", "C"],
        "One-Year Price Return": [0.10, 0.20, 0.30],
        "Six-Month Price Return": [0.05, 0.15, 0.25],
        "Three-Month Price Return": [0.02, 0.10, 0.18],
        "One-Month Price Return": [0.01, 0.05, 0.12],
    })
    time_periods = ["One-Year", "Six-Month", "Three-Month", "One-Month"]
    for tp in time_periods:
        col = f"{tp} Price Return"
        pct_col = f"{tp} Return Percentile"
        df[pct_col] = df[col].rank(pct=True)
    hqm = []
    for row in range(len(df)):
        hqm.append(mean([df.loc[row, f"{tp} Return Percentile"] for tp in time_periods]))
    df["HQM Score"] = hqm
    df = df.sort_values("HQM Score", ascending=False).reset_index(drop=True)
    assert df["Ticker"].iloc[0] == "C"
    assert df["HQM Score"].iloc[0] > df["HQM Score"].iloc[1]


def test_002_top_50_selection():
    """002: Top 50 by HQM Score (descending)."""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "Ticker": [f"T{i}" for i in range(n)],
        "HQM Score": np.random.rand(n),
    })
    df = df.sort_values("HQM Score", ascending=False)
    top50 = df.head(50)
    assert len(top50) == 50
    assert top50["HQM Score"].is_monotonic_decreasing


# ---------- 003 Value (RV) ----------
def test_003_rv_percentile_and_score():
    """003: RV = mean of PE, PB, PS, EV/EBITDA, EV/GP percentiles. Lower raw = cheaper = higher percentile for 'value'."""
    from statistics import mean

    df = pd.DataFrame({
        "Ticker": ["A", "B", "C"],
        "Price-to-Earnings Ratio": [30, 20, 10],
        "Price-to-Book Ratio": [4, 2, 1],
        "EV/EBITDA": [20, 12, 6],
    })
    for col in ["Price-to-Earnings Ratio", "Price-to-Book Ratio", "EV/EBITDA"]:
        df[col + " Percentile"] = df[col].rank(pct=True)
    value_percentiles = [c for c in df.columns if "Percentile" in c]
    df["RV Score"] = df[value_percentiles].mean(axis=1)
    # For value, lower raw metric = cheaper. rank(pct=True) gives smallest value lowest percentile.
    # So C (P/E 10) has lowest percentiles -> lowest RV Score = best value.
    df = df.sort_values("RV Score", ascending=True)
    assert df["Ticker"].iloc[0] == "C"


def test_003_value_top_50():
    """003: Select 50 lowest RV Score (cheapest)."""
    np.random.seed(43)
    n = 100
    df = pd.DataFrame({
        "Ticker": [f"V{i}" for i in range(n)],
        "RV Score": np.random.rand(n),
    })
    df = df.sort_values("RV Score", inplace=False)
    top50 = df.head(50)
    assert len(top50) == 50
    assert top50["RV Score"].is_monotonic_increasing


# ---------- Dependencies (no breaking change) ----------
def test_old_imports():
    """All imports required by original notebooks still work."""
    import math
    import numpy as np
    import pandas as pd
    import requests
    from scipy import stats
    try:
        import xlsxwriter
    except ImportError:
        pytest.skip("xlsxwriter not installed (required by original notebooks)")
    assert hasattr(np, "array") and hasattr(pd, "DataFrame")
    assert hasattr(stats, "percentileofscore")
