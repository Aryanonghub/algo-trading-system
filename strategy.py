import pandas as pd
import numpy as np

print("USING UPDATED STRATEGY FILE")


# ======================================================
# INDICATOR CALCULATION
# ======================================================

def add_indicators(df):
    """
    Adds technical indicators:
    - SMA20
    - SMA50
    - RSI (14 period)
    """

    # ==============================
    # Moving Averages
    # ==============================
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()

    # ==============================
    # RSI (14 period)
    # ==============================
    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df.dropna(inplace=True)

    return df


# ======================================================
# SIGNAL GENERATION (VECTORISED VERSION)
# ======================================================

def generate_signals(df):
    """
    Detects crossover signals:

    BUY  -> SMA20 crosses ABOVE SMA50
    SELL -> SMA20 crosses BELOW SMA50
    """

    if df.empty:
        return pd.DataFrame()

    signals = df.copy()

    # Previous values
    signals["SMA20_prev"] = signals["SMA20"].shift(1)
    signals["SMA50_prev"] = signals["SMA50"].shift(1)

    # BUY condition (Golden Cross)
    buy_condition = (
        (signals["SMA20_prev"] < signals["SMA50_prev"]) &
        (signals["SMA20"] > signals["SMA50"])
    )

    # SELL condition (Death Cross)
    sell_condition = (
        (signals["SMA20_prev"] > signals["SMA50_prev"]) &
        (signals["SMA20"] < signals["SMA50"])
    )

    signals["Signal"] = np.where(buy_condition, "BUY",
                          np.where(sell_condition, "SELL", None))

    # Keep only crossover rows
    signals = signals[signals["Signal"].notna()]

    # Build final output
    output = signals[["Ticker", "Signal", "Close"]].copy()
    output.rename(columns={"Close": "Price"}, inplace=True)
    output["Date"] = signals.index

    # Reorder columns
    output = output[["Date", "Ticker", "Signal", "Price"]]

    return output.reset_index(drop=True)
