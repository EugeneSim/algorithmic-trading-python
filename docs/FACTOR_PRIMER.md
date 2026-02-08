# Factor Investing Primer

## Overview

This document summarizes the theory and practice behind the factors implemented in this repository: **value**, **momentum**, and **quality**. It is intended as educational context for the strategies in the course.

---

## Value

**Idea:** Stocks that are "cheap" relative to fundamentals (earnings, assets, sales, cash flow) tend to outperform over the long run.

**Theoretical basis:**  
- Fama–French: value (e.g. high book-to-market) earns a risk premium.  
- Behavioral: investors overreact to bad news, so value stocks are underpriced.  
- Risk-based: value firms are riskier (distress, cyclicality), so higher expected return.

**Common metrics (lower = cheaper = more value):**
- **P/E** (price-to-earnings): price per dollar of earnings. Fails for negative earnings.
- **P/B** (price-to-book): market value vs book value. Less meaningful for intangibles-heavy firms.
- **P/S** (price-to-sales): useful when earnings are negative or volatile.
- **EV/EBITDA**: enterprise value to operating cash flow; good for cross-sector comparison.
- **EV/GP** (enterprise value to gross profit): less affected by leverage and accounting choices.

**In this repo:** The **RV (Robust Value)** score is the average of percentiles across P/E, P/B, P/S, EV/EBITDA, and EV/GP (lower raw metric → higher percentile → higher RV). We select the top 50 by RV for the value strategy.

---

## Momentum

**Idea:** Stocks that have performed well over the recent past (e.g. 6–12 months) tend to continue performing well in the short term.

**Theoretical basis:**  
- Underreaction to information (earnings, news) so trends persist.  
- Behavioral: herding and slow information diffusion.  
- Risk: momentum as compensation for time-varying risk exposure.

**Common implementations:**
- **Price momentum:** past 2–12 month return (skip most recent month to avoid short-term reversal).
- **High-quality momentum:** require strength across multiple horizons (e.g. 1m, 3m, 6m, 12m) to avoid one-off spikes (e.g. FDA approval).

**In this repo:** **HQM (High-Quality Momentum)** uses 1m, 3m, 6m, and 1y price return percentiles and averages them. Top 50 by HQM form the momentum portfolio. Alternatives implemented: 52-week high proximity, risk-adjusted momentum (return/volatility).

---

## Quality

**Idea:** Profitable, stable, low-leverage firms (high "quality") tend to have higher risk-adjusted returns.

**Common metrics:**
- **ROE** (return on equity): profitability.
- **Earnings stability:** low volatility of earnings over time.
- **Low leverage:** debt/equity or interest coverage.

**In this repo:** Quality is used as an overlay (filter or score) and in the **multi-factor** strategy (value + momentum + quality weights). Quality score can be based on ROE and optional earnings stability.

---

## Multi-Factor Combination

Combining value, momentum, and quality can improve diversification of signals and reduce regime dependence. In this repo, the multi-factor strategy uses configurable weights (e.g. 1/3 value, 1/3 momentum, 1/3 quality), ranks by composite score, and selects the top 50.

---

## Portfolio Construction

- **Equal weight:** simplest; each name has same weight.  
- **Risk parity / volatility weighting:** weight inversely to volatility so each position contributes similarly to risk.  
- **Conviction:** weight by score (e.g. higher HQM or lower RV → higher weight).  
- **Optimization:** minimum variance (minimize portfolio vol) or max Sharpe (maximize risk-adjusted return) subject to constraints.

---

## Backtesting Caveats

- **Survivorship bias:** using only current index members overstates historical returns; use point-in-time constituents when possible.  
- **Look-ahead bias:** ensure all inputs (prices, fundamentals) are available at each rebalance date.  
- **Transaction costs:** rebalancing and turnover reduce net returns; model explicitly for realism.

---

## References (Further Reading)

- Fama, E. F., & French, K. R. (1992). The cross‐section of expected stock returns. *Journal of Finance*.  
- Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*.  
- Asness, C. S., Frazzini, A., & Pedersen, L. H. (2019). Quality minus junk. *Review of Accounting Studies*.
