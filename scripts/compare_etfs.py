#!/usr/bin/env python3
"""
Compare our strategy holdings or style to ETFs (e.g. MTUM, IWD, RPV).
Outputs sector and style comparison if yfinance available.
Usage: python scripts/compare_etfs.py [--strategy-csv output/momentum_strategy.csv]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    parser = argparse.ArgumentParser(description="Compare strategy to ETFs (MTUM, IWD, RPV)")
    parser.add_argument("--strategy-csv", default=None, help="CSV of strategy holdings (Ticker, Weight)")
    parser.add_argument("--etfs", nargs="+", default=["MTUM", "IWD", "RPV"], help="ETF tickers")
    args = parser.parse_args()
    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        print("yfinance required: pip install yfinance")
        return 1
    etfs = args.etfs
    print("ETF comparison (MTUM=momentum, IWD=value, RPV=value)")
    for t in etfs:
        info = yf.Ticker(t).info
        print(f"  {t}: {info.get('longName', t)}")
    # Placeholder: load strategy CSV and compare sector/valuation if we have holdings
    if args.strategy_csv and Path(args.strategy_csv).exists():
        df = pd.read_csv(args.strategy_csv)
        print(f"Strategy holdings: {len(df)} names")
    else:
        print("No strategy CSV provided; run a strategy notebook first and pass --strategy-csv.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
