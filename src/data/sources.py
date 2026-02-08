"""Multiple data sources: IEX Cloud (primary) and yfinance (fallback)."""
import pandas as pd
from typing import List, Optional

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_prices_iex(
    symbols: List[str],
    token: Optional[str] = None,
    batch_size: int = 100,
) -> pd.DataFrame:
    """Fetch quote (price, marketCap) and stats from IEX Cloud. Returns DataFrame with Ticker, Price, Market Capitalization."""
    import requests
    token = token or _get_iex_token()
    if not token:
        raise ValueError("IEX token required. Set IEX_CLOUD_API_TOKEN in secrets.py or env.")
    symbol_list = list(symbols)
    my_columns = ["Ticker", "Price", "Market Capitalization"]
    rows = []
    for chunk in chunks(symbol_list, batch_size):
        sym_str = ",".join(chunk)
        url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={sym_str}&token={token}"
        try:
            data = requests.get(url, timeout=30).json()
        except Exception:
            return pd.DataFrame(columns=my_columns)
        for sym in chunk:
            if sym not in data or "quote" not in data[sym]:
                continue
            q = data[sym]["quote"]
            rows.append({
                "Ticker": sym,
                "Price": q.get("latestPrice"),
                "Market Capitalization": q.get("marketCap"),
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=my_columns)

def get_prices_yfinance(symbols: List[str]) -> pd.DataFrame:
    """Fetch price and market cap from yfinance. Returns same schema as IEX."""
    try:
        import yfinance as yf
    except ImportError:
        return pd.DataFrame(columns=["Ticker", "Price", "Market Capitalization"])
    symbols = [s for s in symbols if s and isinstance(s, str)]
    if not symbols:
        return pd.DataFrame(columns=["Ticker", "Price", "Market Capitalization"])
    data = yf.download(symbols, group_by="ticker", auto_adjust=True, progress=False, threads=True)
    if data.empty:
        return pd.DataFrame(columns=["Ticker", "Price", "Market Capitalization"])
    rows = []
    if len(symbols) == 1:
        data = pd.DataFrame(data).reset_index()
        data.columns = [c if c != "Close" else "Close" for c in data.columns]
        close = data["Close"].iloc[-1] if "Close" in data.columns else None
        ticker = yf.Ticker(symbols[0])
        info = ticker.info
        rows.append({
            "Ticker": symbols[0],
            "Price": close,
            "Market Capitalization": info.get("marketCap"),
        })
    else:
        for sym in symbols:
            try:
                col = "Close" if sym not in data.columns else (sym, "Close") if isinstance(data.columns[0], tuple) else "Close"
                if isinstance(data.columns[0], tuple):
                    close = data[sym]["Close"].iloc[-1] if (sym, "Close") in data.columns else None
                else:
                    close = data["Close"].iloc[-1] if "Close" in data.columns else None
                ticker = yf.Ticker(sym)
                info = ticker.info
                rows.append({
                    "Ticker": sym,
                    "Price": close or info.get("currentPrice"),
                    "Market Capitalization": info.get("marketCap"),
                })
            except Exception:
                continue
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Ticker", "Price", "Market Capitalization"])

def get_prices(
    symbols: List[str],
    primary: str = "iex",
    fallback: str = "yfinance",
    token: Optional[str] = None,
    batch_size: int = 100,
) -> pd.DataFrame:
    """Unified interface: try primary source, then fallback. Returns DataFrame with Ticker, Price, Market Capitalization."""
    if primary == "iex":
        try:
            df = get_prices_iex(symbols, token=token, batch_size=batch_size)
            if not df.empty and df["Price"].notna().any():
                return df
        except Exception:
            pass
        return get_prices_yfinance(symbols)
    else:
        df = get_prices_yfinance(symbols)
        if not df.empty:
            return df
        try:
            return get_prices_iex(symbols, token=token, batch_size=batch_size)
        except Exception:
            return df

def _get_iex_token():
    try:
        from secrets import IEX_CLOUD_API_TOKEN
        return IEX_CLOUD_API_TOKEN
    except ImportError:
        import os
        return os.environ.get("IEX_CLOUD_API_TOKEN")
