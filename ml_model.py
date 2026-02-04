# ml_model.py

import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# =====================================================
# Helper Indicators
# =====================================================

def compute_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def compute_obv(close, volume):
    if close.empty:
        return pd.Series(dtype="float64", index=close.index)

    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


# =====================================================
# Feature Engineering
# =====================================================

def create_features(df):
    required_cols = {"Close", "Volume", "SMA20", "SMA50"}
    if df.empty or not required_cols.issubset(df.columns) or len(df) < 60:
        return df

    macd, _, hist = compute_macd(df["Close"])
    df["MACD"] = macd
    df["MACD_hist"] = hist

    df["OBV"] = compute_obv(df["Close"], df["Volume"])
    df["OBV"] = df["OBV"] / df["Volume"].rolling(20).sum()

    df["ret_1d"] = df["Close"].pct_change()
    df["momentum_5d"] = df["Close"].pct_change(5)
    df["volatility_5d"] = df["ret_1d"].rolling(5).std()

    df["ma_diff"] = df["SMA20"] - df["SMA50"]
    df["price_sma20_diff"] = (df["Close"] - df["SMA20"]) / df["SMA20"].replace(0, np.nan)
    df["price_sma50_diff"] = (df["Close"] - df["SMA50"]) / df["SMA50"].replace(0, np.nan)

    df["ma_crossover"] = (
        (df["SMA20"] > df["SMA50"]) &
        (df["SMA20"].shift(1) <= df["SMA50"].shift(1))
    ).astype(int)

    df["breakout_20d"] = (
        df["Close"] > df["Close"].rolling(20).max().shift(1)
    ).astype(int)

    vol_ma = df["Volume"].rolling(20).mean()
    df["volume_spike"] = (df["Volume"] > 2 * vol_ma).astype(int)

    df["strong_trend"] = (
        (df["SMA20"] > df["SMA50"]) &
        (df["Close"] > df["SMA20"]) &
        (df["Close"] > df["SMA50"])
    ).astype(int)

    df["volume_change"] = df["Volume"].pct_change()
    df["volume_ma_ratio"] = df["Volume"] / vol_ma

    return df


# =====================================================
# ML Training (FIXED PIPELINE)
# =====================================================

def train_ml_model(df):
    logging.info("Training ML model (fixed alignment)")

    if df.empty or "Ticker" not in df.columns:
        return 0.0

    # ---- Create target FIRST ----
    df = df.copy()
    df["target"] = (df.groupby("Ticker")["Close"].shift(-1) > df["Close"]).astype(int)

    feature_cols = [
        "ma_crossover",
        "breakout_20d",
        "volume_spike",
        "strong_trend",
        "momentum_5d",
        "ma_diff",
        "price_sma20_diff",
        "price_sma50_diff",
        "OBV",
        "volume_change",
        "volume_ma_ratio",
        "volatility_5d",
        "MACD",
        "MACD_hist",
    ]

    # ---- Build ONE clean dataframe ----
    df_ml = df[feature_cols + ["target"]]

    # ---- Sanitize ONCE ----
    df_ml = df_ml.replace([np.inf, -np.inf], np.nan).dropna()
    df_ml = df_ml.clip(lower=-1e6, upper=1e6)

    if len(df_ml) < 30:
        logging.warning("Not enough clean data for ML training.")
        return 0.0

    X = df_ml[feature_cols]
    y = df_ml["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test)) * 100
    logging.info(f"ML Model Accuracy: {accuracy:.2f}%")

    return accuracy
