import os
from datetime import datetime
from typing import List, Dict, Any
import time

import requests


YAHOO_SCREENER_URL = "https://query1.finance.yahoo.com/v7/finance/screener/predefined/saved"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v11/finance/quoteSummary/{ticker}"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_json(url: str, params: Dict[str, str] | None = None, retries: int = 3) -> Dict:
    """GET request with basic retry handling."""
    for attempt in range(retries):
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if resp.status_code == 429 and attempt < retries - 1:
            time.sleep(1)
            continue
        resp.raise_for_status()
        return resp.json()
    # if all retries exhausted, raise last error
    resp.raise_for_status()
    return {}


def get_sp500_tickers() -> List[str]:
    """Fetch list of tickers in the S&P 500 index from Yahoo Finance."""
    params = {"scrIds": "SP500"}
    data = fetch_json(YAHOO_SCREENER_URL, params=params)
    quotes = data.get("finance", {}).get("result", [])[0].get("quotes", [])
    return [q["symbol"] for q in quotes]


def get_financial_ratios(ticker: str) -> Dict[str, float]:
    """Retrieve key financial ratios for a given ticker."""
    modules = [
        "defaultKeyStatistics",
        "financialData",
        "price",
    ]
    url = YAHOO_QUOTE_URL.format(ticker=ticker)
    data = fetch_json(url, params={"modules": ",".join(modules)})
    summary = data["quoteSummary"]["result"][0]

    stats = summary.get("defaultKeyStatistics", {})
    fin = summary.get("financialData", {})

    ratios = {
        "pe_ratio": stats.get("trailingPE", {}).get("raw"),
        "pb_ratio": stats.get("priceToBook", {}).get("raw"),
        "de_ratio": fin.get("debtToEquity", {}).get("raw"),
        "roe": fin.get("returnOnEquity", {}).get("raw"),
    }
    return {k: v for k, v in ratios.items() if v is not None}


def get_qualitative_info(ticker: str) -> Dict[str, str]:
    """Fetch qualitative company information."""
    url = YAHOO_QUOTE_URL.format(ticker=ticker)
    modules = ["assetProfile"]
    data = fetch_json(url, params={"modules": ",".join(modules)})
    profile = data["quoteSummary"]["result"][0].get("assetProfile", {})
    return {
        "sector": profile.get("sector"),
        "industry": profile.get("industry"),
        "description": profile.get("longBusinessSummary"),
    }


def compute_value_score(ratios: Dict[str, float]) -> float:
    """Compute a simple score for value investing (lower is better)."""
    score = 0
    weight = {
        "pe_ratio": 0.4,
        "pb_ratio": 0.3,
        "de_ratio": 0.2,
        "roe": -0.1,  # higher ROE reduces score
    }
    for k, w in weight.items():
        val = ratios.get(k)
        if val is not None:
            score += w * val
    return score


def rank_stocks(tickers: List[str]) -> List[Dict[str, Any]]:
    """Rank tickers by value score."""
    ranking = []
    for ticker in tickers:
        try:
            ratios = get_financial_ratios(ticker)
            info = get_qualitative_info(ticker)
            score = compute_value_score(ratios)
            ranking.append({
                "ticker": ticker,
                "score": score,
                "ratios": ratios,
                "info": info,
            })
            time.sleep(0.5)
        except Exception as e:
            print(f"Skipping {ticker}: {e}")
            continue
    ranking.sort(key=lambda x: x["score"])
    return ranking


def save_markdown(top_stocks: List[Dict[str, Any]]) -> str:
    """Save ranking result to a markdown file in _posts/."""
    today = datetime.today().strftime("%Y-%m-%d")
    filename = f"{today}-value-investing-picks.md"
    filepath = os.path.join("_posts", filename)

    lines = [
        "---",
        "title: \"Top 5 Value Investing Stocks\"",
        f"date: {today}",
        "layout: post",
        "---",
        "",
        "## Top Stocks",
    ]

    for i, stock in enumerate(top_stocks, 1):
        ratios_text = ", ".join(f"{k}: {v}" for k, v in stock["ratios"].items())
        info = stock["info"]
        description = info.get("description", "").split(". ")[0] + "."
        lines.append(f"{i}. **{stock['ticker']}** ({info.get('sector', '')} - {info.get('industry', '')})")
        lines.append(f"   - {ratios_text}")
        lines.append(f"   - {description}")

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    return filepath


def main():
    tickers = get_sp500_tickers()
    ranking = rank_stocks(tickers)
    top5 = ranking[:5]
    path = save_markdown(top5)
    print(f"Saved results to {path}")


if __name__ == "__main__":
    main()
