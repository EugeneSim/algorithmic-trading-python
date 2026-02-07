"""Universe loading with optional survivorship-bias awareness."""
import pandas as pd
from pathlib import Path
from typing import List, Optional

def load_universe(constituents_file: Optional[str] = None, base_path: Optional[Path] = None) -> pd.DataFrame:
    """Load constituent list (e.g. S&P 500). Returns DataFrame with at least 'Ticker' column."""
    base = base_path or Path(__file__).resolve().parent.parent.parent
    path = Path(constituents_file) if constituents_file else base / "starter_files" / "sp_500_stocks.csv"
    if not path.is_absolute():
        path = base / path
    for candidate in [path, base / "sp_500_stocks.csv", base / "starter_files" / "sp_500_stocks.csv"]:
        if candidate.exists():
            df = pd.read_csv(candidate)
            if "Ticker" not in df.columns and len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: "Ticker"})
            return df
    return pd.DataFrame(columns=["Ticker"])

def load_universe_survivorship_aware(
    constituents_file: Optional[str] = None,
    as_of_date: Optional[str] = None,
    delisted_file: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load universe with survivorship-bias awareness.
    When point-in-time constituent data is available, pass as_of_date and optional delisted list.
    For now, falls back to load_universe() and documents the limitation.
    """
    df = load_universe(constituents_file=constituents_file)
    if as_of_date or delisted_file:
        # Placeholder: when you have point-in-time constituents or delisted tickers,
        # filter df by as_of_date and merge delisted_file so backtests include delisted names.
        pass
    return df

def get_ticker_list(constituents_file: Optional[str] = None) -> List[str]:
    """Return list of ticker symbols."""
    df = load_universe(constituents_file=constituents_file)
    if "Ticker" in df.columns:
        return df["Ticker"].dropna().astype(str).str.strip().tolist()
    return []
