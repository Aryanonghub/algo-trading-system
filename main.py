"""
main.py

Core trading pipeline logic for the Telegram Bot and Streamlit UI.

This module:
- Downloads historical stock data
- Calculates technical indicators (SMA20, SMA50, RSI)
- Detects crossover signals (BUY / SELL)
- Returns summary statistics
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

from utils import setup_logging
from strategy import add_indicators, generate_signals


# ======================================================
# CONFIGURATION
# ======================================================

# Number of days of historical data to scan
DATA_LOOKBACK_DAYS = 365   # 1 Year


# ======================================================
# MAIN TRADING PIPELINE
# ======================================================

def run_trading_pipeline(ticker: str) -> dict:
    """
    Runs the full trading pipeline for a single stock ticker.

    Parameters:
        ticker (str): Stock symbol (e.g., "RELIANCE.NS")

    Returns:
        dict:
            {
                "total_crossovers": int,
                "last_5_crossovers": list,
                "summary": dict
            }
    """

    logger = setup_logging()
    logger.info(f"Running pipeline for {ticker}")

    # --------------------------------------------------
    # STEP 1: Download Historical Data
    # --------------------------------------------------

    end_date = datetime.now()
    start_date = end_date - timedelta(days=DATA_LOOKBACK_DAYS)

    try:
        df = yf.download(ticker, start=start_date, end=end_date)

        # Fix MultiIndex columns (sometimes returned by yfinance)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            logger.warning("Downloaded DataFrame is empty.")
            return {
                "total_crossovers": 0,
                "last_5_crossovers": [],
                "summary": None
            }

    except Exception as e:
        logger.error(f"Data download failed: {e}")
        return {
            "total_crossovers": 0,
            "last_5_crossovers": [],
            "summary": None
        }

    # Add ticker column for identification
    df["Ticker"] = ticker

    # --------------------------------------------------
    # STEP 2: Add Technical Indicators
    # --------------------------------------------------

    df = add_indicators(df)

    # --------------------------------------------------
    # STEP 3: Generate Crossover Signals
    # --------------------------------------------------

    signals = generate_signals(df)

    if signals.empty:
        total_crossovers = 0
        all_crossovers = []
    else:
        # Ensure Date column is datetime
        signals["Date"] = pd.to_datetime(signals["Date"])

        # Sort by latest first
        signals_sorted = signals.sort_values(by="Date", ascending=False)

        total_crossovers = len(signals_sorted)

        # Convert all crossover rows to clean dictionary format
        all_crossovers = []

        for _, row in signals_sorted.iterrows():
            all_crossovers.append({
                "Date": row["Date"].strftime("%Y-%m-%d"),
                "Signal": row["Signal"],
                "Price": float(row["Price"])
            })

    # --------------------------------------------------
    # STEP 4: Build Summary Statistics
    # --------------------------------------------------

    current_price = float(df["Close"].iloc[-1])
    highest_price = float(df["High"].max())
    lowest_price = float(df["Low"].min())

    summary = {
        "current_price": round(current_price, 2),
        "highest_price": round(highest_price, 2),
        "lowest_price": round(lowest_price, 2),
        "data_period_days": DATA_LOOKBACK_DAYS
    }

    # --------------------------------------------------
    # FINAL RETURN STRUCTURE
    # --------------------------------------------------

    return {
        "total_crossovers": total_crossovers,
        "last_5_crossovers": all_crossovers,  # contains ALL crossovers
        "summary": summary
    }


# ======================================================
# LOCAL TESTING
# ======================================================

if __name__ == "__main__":
    result = run_trading_pipeline("RELIANCE.NS")
    print(result)
