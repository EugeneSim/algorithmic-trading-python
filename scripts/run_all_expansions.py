#!/usr/bin/env python3
"""
Run all expansion features: multi-factor, sector, quality, alt momentum/value,
risk parity, min-var, max-Sharpe, conviction, correlation, dashboard.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np

def main():
    from src.config_loader import load_config
    from src.data import load_universe, get_prices
    from src.scoring import compute_hqm_score, compute_rv_score, compute_quality_score, quality_filter
    from src.scoring.momentum import compute_52w_high_proximity, compute_risk_adjusted_momentum
    from src.scoring.value import compute_alternative_value_metrics
    from src.portfolio import weights_equal, weights_risk_parity, weights_conviction, weights_min_variance, weights_max_sharpe, apply_weight_bounds
    from src.portfolio.sector import apply_sector_neutral, apply_sector_tilt
    from src.reports import build_dashboard_html, correlation_report

    config = load_config()
    print("Config loaded:", list(config.keys()))

    # Load universe (sample)
    df = load_universe()
    tickers = df["Ticker"].dropna().astype(str).tolist()[:30]
    if not tickers:
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "JPM", "V", "WMT", "PG", "JNJ"]
    print("Universe sample size:", len(tickers))

    # Synthetic data for demo (no API calls required)
    n = len(tickers)
    np.random.seed(42)
    prices = pd.DataFrame({
        "Ticker": tickers,
        "Price": np.random.uniform(20, 400, n),
        "One-Year Price Return": np.random.uniform(-0.3, 0.8, n),
        "Six-Month Price Return": np.random.uniform(-0.2, 0.5, n),
        "Three-Month Price Return": np.random.uniform(-0.15, 0.3, n),
        "One-Month Price Return": np.random.uniform(-0.1, 0.2, n),
        "Price-to-Earnings Ratio": np.random.uniform(10, 40, n),
        "Price-to-Book Ratio": np.random.uniform(1, 8, n),
        "Price-to-Sales Ratio": np.random.uniform(0.5, 5, n),
        "EV/EBITDA": np.random.uniform(5, 25, n),
        "EV/GP": np.random.uniform(2, 15, n),
        "ROE": np.random.uniform(0.05, 0.25, n),
        "Volatility_12m": np.random.uniform(0.15, 0.45, n),
        "Sector": np.random.choice(["Technology", "Healthcare", "Financials", "Consumer"], n),
    })

    # Multi-factor: HQM + RV + Quality
    mom = compute_hqm_score(prices)
    val = compute_rv_score(prices)
    qual = compute_quality_score(prices, roe_col="ROE")
    mom["HQM Score"] = mom.get("HQM Score", mom.get("One-Year Price Return", 0))
    val["RV Score"] = val.get("RV Score", 0.5)
    qual["Quality Score"] = qual.get("Quality Score", 0.5)
    prices["HQM Score"] = mom["HQM Score"]
    prices["RV Score"] = val["RV Score"]
    prices["Quality Score"] = qual["Quality Score"]
    prices["Composite Score"] = (
        0.33 * prices["RV Score"].rank(pct=True) +  # value: lower RV = better, so rank
        0.33 * prices["HQM Score"] +
        0.34 * prices["Quality Score"]
    )
    top_multi = prices.nlargest(10, "Composite Score")[["Ticker", "Price", "Composite Score"]]
    print("Multi-factor top 10:")
    print(top_multi.to_string())

    # Sector-neutral / tilt
    sector_weights = apply_sector_neutral(prices, sector_col="Sector")
    print("Sector-neutral weights sample:", sector_weights[["Ticker", "Weight"]].head(5).to_string())
    tilted = apply_sector_tilt(prices.copy(), sector_col="Sector", tilt={"Technology": 1.2, "Healthcare": 0.8})
    print("Sector tilt applied.")

    # Quality overlay
    filtered = quality_filter(prices, min_roe=0.10, roe_col="ROE")
    print("Quality filter (ROE>=10%):", len(filtered), "of", len(prices))

    # Alternative momentum: 52w high
    prices["52w_high"] = prices["Price"] * np.random.uniform(1.0, 1.3, n)
    prices["52w_high_proximity"] = prices["Price"] / prices["52w_high"]
    print("52w high proximity sample:", prices[["Ticker", "52w_high_proximity"]].head(3).to_string())

    # Alternative value
    alt = compute_alternative_value_metrics(25.0, 4.0, 100.0, free_cash_flow=5.0, dividend_per_share=2.0)
    print("Alternative value metrics (sample):", alt)

    # Weighting: risk parity, conviction, min-var, max-Sharpe
    vol = prices["Volatility_12m"].values
    w_rp = weights_risk_parity(vol)
    w_conv = weights_conviction(prices["Composite Score"].values, power=1.0)
    cov = np.cov(np.random.randn(100, n).T)
    w_minv = weights_min_variance(cov)
    mu = prices["One-Year Price Return"].values[:n]
    w_ms = weights_max_sharpe(mu, cov)
    w_conv = apply_weight_bounds(w_conv, 0.005, 0.10)
    print("Risk parity sum:", w_rp.sum(), "Conviction sum:", w_conv.sum())

    # Correlation report (use random returns)
    rets = pd.DataFrame(np.random.randn(252, n) * 0.01, columns=tickers[:n])
    corr_rep = correlation_report(rets)
    print("Correlation report: avg_corr=%.3f, hhi=%.4f" % (corr_rep["avg_correlation"], corr_rep["hhi"]))

    # Dashboard
    portfolio = prices.head(10)[["Ticker", "Price"]].copy()
    portfolio["Weight"] = 0.1
    html = build_dashboard_html(
        portfolio,
        strategy_name="Expansion Demo",
        metrics={
            "avg_correlation": round(corr_rep["avg_correlation"], 4),
            "hhi": round(corr_rep["hhi"], 4),
            "n_assets": corr_rep["n_assets"],
        },
        output_path=str(ROOT / "reports" / "dashboard.html"),
    )
    Path(ROOT / "reports").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "reports" / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Dashboard written to reports/dashboard.html")

    print("All expansion features executed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
