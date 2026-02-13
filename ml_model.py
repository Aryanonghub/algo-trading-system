"""
ml_model.py

Machine Learning pipeline for stock movement prediction.

This module:
- Creates technical features (MACD, OBV, momentum, volatility, etc.)
- Builds a binary classification target (next-day up/down)
- Trains a RandomForest model
- Returns prediction accuracy
"""

import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# =====================================================
# HELPER INDICATORS
# =====================================================

def compute_macd(close, fast=12, slow=26, signal=9):
    """
    Compute MACD indicator.

    Returns:
        macd_line, signal_line, histogram
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def compute_obv(close, volume):
    """
    Compute On-Balance Volume (OBV).
    """
    if close.empty:
        return pd.Series(dtype="float64", index=close.index)

    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()


# =====================================================
# FEATURE ENGINEERING
# =====================================================

def create_features(df):
    """
    Adds technical and momentum-based features to DataFrame.
    """

    required_cols = {"Close", "Volume", "SMA20", "SMA50"}

    if df.empty or not required_cols.issubset(df.columns) or len(df) < 60:
        return df

    # -------------------------
    # Trend Indicators
    # -------------------------

    macd, _, hist = compute_macd(df["Close"])
    df["MACD"] = macd
    df["MACD_hist"] = hist

    df["OBV"] = compute_obv(df["Close"], df["Volume"])
    df["OBV"] = df["OBV"] / df["Volume"].rolling(20).sum()

    # -------------------------
    # Price-Based Features
    # -------------------------

    df["ret_1d"] = df["Close"].pct_change()
    df["momentum_5d"] = df["Close"].pct_change(5)
    df["volatility_5d"] = df["ret_1d"].rolling(5).std()

    df["ma_diff"] = df["SMA20"] - df["SMA50"]
    df["price_sma20_diff"] = (
        df["Close"] - df["SMA20"]
    ) / df["SMA20"].replace(0, np.nan)

    df["price_sma50_diff"] = (
        df["Close"] - df["SMA50"]
    ) / df["SMA50"].replace(0, np.nan)

    # -------------------------
    # Event-Based Signals
    # -------------------------

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
# ML TRAINING PIPELINE
# =====================================================

def train_ml_model(df):
    """
    Train a RandomForest classifier to predict next-day movement.

    Returns:
        Accuracy (%) as float
    """

    logging.info("Training ML model...")

    if df.empty or "Ticker" not in df.columns:
        return 0.0

    df = df.copy()

    # -------------------------------------------------
    # STEP 1: Create Target Variable
    # -------------------------------------------------
    # 1 if next day price > today price else 0
    df["target"] = (
        df.groupby("Ticker")["Close"].shift(-1) > df["Close"]
    ).astype(int)

    # -------------------------------------------------
    # STEP 2: Select Features
    # -------------------------------------------------

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

    df_ml = df[feature_cols + ["target"]]

    # -------------------------------------------------
    # STEP 3: Data Cleaning
    # -------------------------------------------------

    df_ml = df_ml.replace([np.inf, -np.inf], np.nan).dropna()
    df_ml = df_ml.clip(lower=-1e6, upper=1e6)

    if len(df_ml) < 30:
        logging.warning("Not enough clean data for ML training.")
        return 0.0

    X = df_ml[feature_cols]
    y = df_ml["target"]

    # Time-series split (no shuffle)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        shuffle=False
    )

    # -------------------------------------------------
    # STEP 4: Train Model
    # -------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # -------------------------------------------------
    # STEP 5: Evaluate Model
    # -------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        model.predict(X_test)
    ) * 100

    logging.info(f"ML Model Accuracy: {accuracy:.2f}%")

    return accuracy
