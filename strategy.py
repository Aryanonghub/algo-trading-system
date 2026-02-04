import pandas as pd
import numpy as np


def add_indicators(df):
    """
    Calculates and adds technical indicators (RSI, SMA20, SMA50) to the DataFrame.
    """

    # === Simple Moving Averages ===
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()

    # === RSI (14-period, Wilder’s method) ===
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df.dropna(inplace=True)
    return df


def generate_signals(df):
    """
    Implements the trading strategy to generate buy signals.
    - Buy Signal: 20-SMA crosses above 50-SMA
    """

    signals = []

    for i in range(1, len(df)):
        current_row = df.iloc[i]
        prev_row = df.iloc[i - 1]

        # Golden crossover condition
        crossover_condition = (
            prev_row["SMA20"] < prev_row["SMA50"]
            and current_row["SMA20"] > current_row["SMA50"]
        )

        if crossover_condition:
            trade_info = {
                "Date": current_row.name,
                "Ticker": current_row["Ticker"],
                "Signal": "BUY",
                "Price": current_row["Close"],
            }
            signals.append(trade_info)

    return pd.DataFrame(signals)
