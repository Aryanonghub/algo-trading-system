
## 📌 Project Summary (Algorithmic Trading System)

This project is an **event-driven algorithmic trading analysis system** built using **Python, Machine Learning, and Streamlit**.
It analyzes **NIFTY 50 equity data**, converts raw market information into **explainable trading events** (trend shifts, breakouts, volume confirmation, momentum, volatility), and uses a **RandomForest ML model** to estimate the **probability of next-day price movement**.

The system emphasizes **interpretability over black-box predictions** and demonstrates strong software engineering practices, including clean feature engineering, data sanitization, modular design, and end-to-end pipeline integration. Results are visualized through an **interactive Streamlit dashboard**, logged to **Google Sheets**, and can be queried via a **Telegram bot**.

**Key skills demonstrated**:

* Machine Learning on financial time-series (RandomForest)
* Feature engineering & data pipelines
* Event-based market modeling (no RSI / fragile indicators)
* Streamlit dashboards & visualization
* API integrations (yfinance, Google Sheets, Telegram)
* Production-safe data handling & debugging

---
# 📈 Algorithmic Trading System

**(Python · Streamlit · Event-Based ML)**

A prototype **algorithmic trading & analysis system** for **NIFTY 50 equities**, designed to be:

* **Explainable** (event-based signals, not black-box indicators)
* **ML-assisted** (probability-based, not auto-trading)
* **Engineer-friendly** (clean pipeline, no fragile dependencies)

---

## 🧠 What This System Does (In One Paragraph)

This system ingests daily OHLCV data, derives **event-based market features** (trend shifts, breakouts, volume confirmation, momentum, volatility), and trains a **RandomForest classifier** to estimate the **probability of next-day price movement**.
The ML model does **not auto-trade** — it supports decision-making by ranking market conditions that historically led to upward moves. Results are visualized via **Streamlit**, logged to **Google Sheets**, and can optionally be queried via **Telegram**.

---

## 🚀 Key Features

* **Automated Data Ingestion** — Daily OHLCV data via `yfinance`
* **Event-Based Strategy Engine**

  * SMA(20/50) crossover
  * 20-day price breakout
  * Volume spike & trend confirmation
* **ML Prediction Layer (RandomForest)**

  * Predicts **next-day direction probability**
  * Uses explainable, event-based features (no RSI)
* **Google Sheets Logging**

  * Signal snapshots
  * Model outputs
  * Trade journaling
* **Interactive Streamlit Dashboard**

  * Multi-ticker analysis
  * Feature visualization
* **Optional Telegram Interface**

  * Query signals & highlights

---

## 🧠 ML Model Overview (High Level)

**Problem Type**: Supervised classification
**Target**:

```
1 → Tomorrow’s close > Today’s close
0 → Otherwise
```

**Model**: RandomForestClassifier
**Why RandomForest**:

* Handles non-linear feature interactions
* No feature scaling required
* Robust on tabular financial data
* Produces stable probability estimates

---

## 🧩 Feature Groups Used for Prediction

### 1️⃣ Trend & Structure

* `ma_crossover`
* `strong_trend`
* `ma_diff`

### 2️⃣ Breakout & Price Action

* `breakout_20d`
* `price_sma20_diff`
* `price_sma50_diff`

### 3️⃣ Volume Confirmation

* `volume_spike`
* `volume_ma_ratio`
* `volume_change`
* `OBV` (normalized)

### 4️⃣ Momentum

* `momentum_5d`
* `MACD`
* `MACD_hist`

### 5️⃣ Risk / Regime

* `volatility_5d`

👉 Each trading day is treated as a **market snapshot**, and the model learns which combinations of these features historically led to upward moves.

---

## 🛠️ Tech Stack

* **Language**: Python ≥ 3.10
* **Data**: `yfinance`
* **ML**: scikit-learn (RandomForest)
* **UI**: Streamlit, Plotly
* **Sheets API**: gspread, oauth2client
* **Alerts (Optional)**: Telegram Bot API

> ❌ No `pandas-ta`
> ❌ No RSI
> ✅ Fully dependency-stable

---

## 📂 Project Structure

```
algo-trading-system/
├── main.py            # End-to-end pipeline runner
├── ui.py              # Streamlit dashboard
├── strategy.py        # Event-based signal logic (SMA, breakout, volume)
├── ml_model.py        # Feature engineering + ML training
├── sheets.py          # Google Sheets logging
├── utils.py           # Logging & Telegram helpers
├── requirements.txt   # Dependencies
└── credentials.json   # Google service account key (gitignored)
```

---

## ⚡ Quick Start

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Aryanonghub/algo-trading-system.git
cd algo-trading-system
```

### 2️⃣ Create & activate a virtual environment

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Option A — Streamlit Dashboard (Recommended)

```bash
python -m streamlit run ui.py
```

* Select tickers & date range
* View signals, features, and ML accuracy
* Inspect event highlights per stock

### Option B — CLI Pipeline

```bash
python main.py
```

* Runs the full pipeline
* Logs outputs to Google Sheets

---

## 📊 Google Sheets Output

* **Signal Snapshots** — Event flags per day
* **ML Outputs** — Accuracy & prediction metadata
* **Trade Journal** — Optional backtest logs

---

## 🔔 Optional Telegram Integration

* Query signals (e.g. breakouts, strong trends)
* Receive daily highlights
* Designed for **explainability**, not spam alerts

---

## 🧭 System Architecture (Conceptual)

```
[Streamlit UI]
      |
      v
[Data Fetcher (yfinance)]
      |
      v
[Event-Based Feature Engine]
      |
      +--> [Google Sheets Logging]
      |
      +--> [Telegram Queries]
      |
      v
[ML Model (RandomForest)]
      |
      v
[Probability Estimates + UI]
```

---

## 🛠️ Troubleshooting

* **Empty data** → Check ticker format (e.g. `RELIANCE.NS`)
* **Low ML accuracy** → Normal for financial data (55–65% is strong)
* **Google auth issues** → Verify `credentials.json` & sheet sharing
* **No signals** → Market conditions may not meet event thresholds

---

## 📅 Roadmap

* Probability-based signal ranking
* Feature importance export (Sheets)
* Walk-forward validation
* Backtesting engine (PnL, drawdown)
* Position sizing & risk management
* Live broker integration (Zerodha / Upstox)
* Dockerization
* Unit & data integrity tests

---

## ⚠️ Disclaimer

**Educational & research use only.**
This system is not financial advice.
Markets involve risk; past behavior does not guarantee future outcomes.

---

If you want, I can also:

* ✍️ Write a **short README summary** for recruiters
* 📊 Add **feature importance explanation section**
* 🧠 Add **“How to interpret predictions”** for non-ML users

