"""Load and validate strategy configuration from YAML/JSON."""
import os
from pathlib import Path

def load_config(config_path=None):
    """Load config from YAML or JSON. Returns dict."""
    if config_path is None:
        base = Path(__file__).resolve().parent.parent
        for name in ("config/strategy_config.yaml", "config/strategy_config.json"):
            p = base / name
            if p.exists():
                config_path = p
                break
    if config_path is None:
        return _default_config()
    path = Path(config_path)
    if not path.exists():
        return _default_config()
    suffix = path.suffix.lower()
    if suffix == ".yaml" or suffix == ".yml":
        try:
            import yaml
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or _default_config()
        except Exception:
            return _default_config()
    if suffix == ".json":
        try:
            import json
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return _default_config()
    return _default_config()

def _default_config():
    return {
        "universe": {"name": "S&P 500", "constituents_file": "sp_500_stocks.csv"},
        "data": {"primary": "iex", "fallback": "yfinance", "batch_size": 100},
        "strategies": {
            "equal_weight": {"enabled": True, "top_n": None},
            "momentum": {"enabled": True, "top_n": 50},
            "value": {"enabled": True, "top_n": 50},
            "multi_factor": {"enabled": True, "top_n": 50},
        },
        "portfolio": {"weighting": "equal", "min_weight": 0.005, "max_weight": 0.10},
        "backtest": {"rebalance_freq": "M", "initial_capital": 100000},
        "output": {"excel_dir": "output", "report_dir": "reports"},
    }
