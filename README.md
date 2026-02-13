# 📈 Algorithmic Trading System

**Python · Streamlit · Event-Based ML · Telegram Integration**

---

## 📌 Project Overview

This project is an **event-driven algorithmic trading analysis system** built using **Python, Machine Learning, and Streamlit**.

It analyzes **NIFTY 50 equity data**, transforms raw OHLCV market data into **interpretable trading events**, and uses a **RandomForest classifier** to estimate the **probability of next-day price movement**.

Unlike black-box trading systems, this project prioritizes:

* ✅ Explainability
* ✅ Feature transparency
* ✅ Modular architecture
* ✅ Production-safe data handling

Outputs are visualized through an **interactive Streamlit dashboard**, logged to **Google Sheets**, and optionally accessible via a **Telegram bot interface**.

---

## 🧠 What This System Does (In One Paragraph)

The system ingests daily stock data, engineers event-based features (trend shifts, breakouts, volume confirmation, momentum, volatility), and trains a **RandomForest model** to predict the probability that tomorrow’s closing price will be higher than today’s.

The model does **not auto-trade**.
It provides probabilistic decision support to help evaluate favorable market conditions.

---

## 🚀 Core Capabilities

### 📊 1. Automated Data Pipeline

* Daily OHLCV data via `yfinance`
* Data sanitization & preprocessing
* Multi-ticker support

### 📈 2. Event-Based Strategy Engine

Signals are derived from structural market conditions:

* SMA (20/50) crossover detection
* 20-day breakout logic
* Volume spike & trend confirmation
* Momentum & volatility regime detection

No fragile RSI-based heuristics.

---

### 🤖 3. Machine Learning Layer

* **Model**: RandomForestClassifier
* **Problem Type**: Supervised classification
* **Target Variable**:

```
1 → Tomorrow’s Close > Today’s Close  
0 → Otherwise
```

Why RandomForest?

* Handles non-linear interactions
* No feature scaling required
* Stable on tabular financial data
* Produces reliable probability estimates

---

### 📊 4. Interactive Streamlit Dashboard

* Multi-ticker selection
* Backtesting over custom date ranges
* Visualized SMA crossovers
* Buy/Sell markers
* ML accuracy display
* Indicator overlays using Plotly

---

### 📄 5. Google Sheets Logging
Not Working!
* Signal snapshots
* Model accuracy tracking
* Optional trade journal logging

---

### 🔔 6. Telegram Bot (Optional)

* Query crossover events
* View stock summaries
* Get signal breakdowns
* Designed for explainable outputs (not spam alerts)

---

## 🧩 Feature Groups Used for Prediction

Each trading day is treated as a **market snapshot**.

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
* Normalized OBV

### 4️⃣ Momentum

* `momentum_5d`
* `MACD`
* `MACD_hist`

### 5️⃣ Risk / Regime

* `volatility_5d`

The model learns which combinations historically led to upward movement.

---

## 🛠️ Tech Stack

| Layer    | Technology                  |
| -------- | --------------------------- |
| Language | Python ≥ 3.10               |
| Data     | yfinance                    |
| ML       | scikit-learn (RandomForest) |
| UI       | Streamlit + Plotly          |
| Logging  | Google Sheets (gspread)     |
| Alerts   | Telegram Bot API            |

**Design Choices:**

* ❌ No `pandas-ta`
* ❌ No RSI
* ✅ Stable dependency structure
* ✅ Fully modular architecture

---

## 📂 Project Structure

```
algo-trading-system/
│
├── main.py          # End-to-end pipeline
├── ui.py            # Streamlit dashboard
├── strategy.py      # Event-based signal logic
├── ml_model.py      # Feature engineering + ML model
├── sheets.py        # Google Sheets logging
├── bot.py           # Telegram bot integration
├── utils.py         # Logging utilities
├── requirements.txt
└── .gitignore
```

---

## ⚡ Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Aryanonghub/algo-trading-system.git
cd algo-trading-system
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Running the System

### ▶ Streamlit Dashboard (Recommended)

```bash
python -m streamlit run ui.py
```

### ▶ CLI Pipeline

```bash
python main.py
```

### ▶ Telegram Bot

```bash
python bot.py
```

Make sure to set:

```
export BOT_TOKEN=your_telegram_token
```

---

## 🧭 Conceptual Architecture

```
[Streamlit UI]
        |
        v
[Data Fetcher - yfinance]
        |
        v
[Feature Engineering Engine]
        |
        +--> Google Sheets Logging
        +--> Telegram Queries
        |
        v
[RandomForest Model]
        |
        v
[Probability Output + Visual Dashboard]
```

---

## 📊 Expected ML Accuracy

Financial prediction is inherently noisy.

Typical realistic accuracy:

```
55% – 65%
```

Anything consistently above this in live conditions is strong.

---

## 📅 Roadmap

* Walk-forward validation
* Feature importance export
* Full backtesting engine (PnL, drawdown)
* Position sizing logic
* Risk management module
* Dockerization
* Unit testing
* Broker API integration (Zerodha / Upstox)

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.

It does not constitute financial advice.
Trading involves risk. Past performance does not guarantee future results.

---
