# In ml_model.py

import pandas as pd
import pandas_ta as ta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import logging


def create_features(df):
    """
    Calculates and adds all ML features to a DataFrame for a SINGLE stock.
    """
    df.ta.macd(append=True)
    df.ta.obv(append=True)
    df['ma_diff'] = df['SMA20'] - df['SMA50']
    df['price_change_1d'] = df['Close'].pct_change(1)
    df.dropna(inplace=True)
    return df


def create_target(df):
    """
    Create the target variable for predicting next day movement.
    """
    # Important: Group by Ticker before shifting to prevent data leakage
    df['target'] = df.groupby('Ticker')['Close'].transform(
        lambda x: (x.shift(-1) > x).astype(int))
    df.dropna(inplace=True)
    return df


def train_ml_model(df_with_features):
    """
    Trains a model using a DataFrame that already has features calculated.
    """
    logging.info("Starting ML model training with added features...")
    df_with_target = create_target(df_with_features)

    if df_with_target.empty:
        logging.warning("Not enough data to train ML model.")
        return 0.0

    features = ['RSI', 'ma_diff', 'MACD_12_26_9', 'OBV', 'Volume']
    X = df_with_target[features]
    y = df_with_target['target']

    if len(X) < 10:
        logging.warning("Not enough data to split for training and testing.")
        return 0.0

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False)

    model = RandomForestClassifier(
        n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100

    logging.info(f"ML Model Prediction Accuracy: {accuracy:.2f}%")
    return accuracy
