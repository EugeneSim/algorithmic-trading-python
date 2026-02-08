#!/usr/bin/env python3
"""
Periodic rebalance script: run screening, compare to current portfolio, output trade list.
Usage: python scripts/rebalance.py [--config config/strategy_config.yaml] [--portfolio current_holdings.csv]
"""
import argparse
import sys
from pathlib import Path

# Add project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

def load_config(config_path=None):
    from src.config_loader import load_config as _load
    return _load(config_path)

def main():
    parser = argparse.ArgumentParser(description="Rebalance: output recommended trades")
    parser.add_argument("--config", default=None, help="Path to strategy config YAML/JSON")
    parser.add_argument("--portfolio", default=None, help="CSV of current holdings (Ticker, Shares)")
    parser.add_argument("--value", type=float, default=100_000, help="Portfolio value for sizing")
    parser.add_argument("--out", default=None, help="Output CSV path for trade list")
    args = parser.parse_args()
    config = load_config(args.config)
    # Placeholder: in full implementation would run screening (momentum/value) and compute target weights
    # then diff vs current to get trade list
    target_cols = ["Ticker", "Action", "Shares", "Target_Weight", "Current_Weight"]
    trade_list = pd.DataFrame(columns=target_cols)
    out_path = args.out or str(ROOT / "output" / "rebalance_trades.csv")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    trade_list.to_csv(out_path, index=False)
    print(f"Trade list (placeholder) written to {out_path}. Run full pipeline from notebooks for actual screening.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
