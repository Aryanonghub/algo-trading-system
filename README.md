# 📈 Algorithmic Trading System (Python + Streamlit + ML)

A prototype **algorithmic trading system** for the **NIFTY 50** that:

- Fetches equity data via **yfinance**
- Generates **trading signals** using RSI + SMA crossover
- Backtests with a 15-day exit rule
- Logs results to **Google Sheets**
- Trains an **ML model (RandomForest)** to predict next-day price movement
- Provides an **interactive Streamlit dashboard** for analysis
- (Optional) Sends alerts via Telegram

---

## 🚀 Features

- **Automated Data Ingestion** — Daily OHLCV data from `yfinance`
- **Strategy Engine** — RSI + SMA(20/50) crossover buy logic, 15-day exit assumption
- **ML Predictions** — RandomForest using RSI, MACD, OBV, volume, MA-diff, % change
- **Google Sheets Logging** — Trade journal, P&L summary, win ratio
- **Interactive UI** — Streamlit dashboard for multi-ticker backtests & charts
- **Optional Alerts** — Telegram bot notifications

---

## 🛠️ Tech Stack

- **Core**: Python ≥ 3.10, pandas, numpy
- **Data**: `yfinance`
- **Indicators**: `pandas-ta`
- **ML**: scikit-learn (RandomForest)
- **UI**: Streamlit, Plotly
- **Sheets API**: gspread, oauth2client
- **Alerts (Optional)**: python-telegram-bot

---

## 📂 Project Structure

```

algo-trading-system/
├── main.py           # Core pipeline: fetch → indicators → signals → ML → Sheets
├── ui.py             # Streamlit dashboard
├── strategy.py       # RSI + SMA strategy & signal generation
├── ml\_model.py       # Feature engineering + ML training/eval
├── sheets.py         # Google Sheets auth + logging
├── utils.py          # Logging + Telegram alert helper
├── requirements.txt  # Python dependencies
└── credentials.json  # Google service account key (not committed)

````

---

## ⚡ Quick Start

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Aryanonghub/algo-trading-system.git
cd algo-trading-system
````

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
# In case of version conflicts:
pip install "numpy==1.26.4"
```

### 4️⃣ Google Sheets API Setup

1. Create a **Google Cloud Project**
2. Enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** (Editor role)
4. Generate a JSON key → Save as `credentials.json` in project root
5. Share your Google Sheet with the service account email (Editor access)

---

## 💻 Usage

### Option A — Interactive Dashboard (Recommended)

```bash
streamlit run ui.py
```

* Select tickers and date range in the sidebar
* Click **Run Analysis** to generate signals, charts & predictions

### Option B — CLI Backtesting

```bash
python main.py
```

* Runs backtest using defaults in `main.py`
* Logs trades and P\&L to Google Sheets

---

## 📊 Google Sheets Output

* **Trades/Signals** — Buy events with dates & prices
* **P\&L Summary** — Aggregated results
* **Win Ratio** — Strategy performance stats

---

## 🔔 Optional Telegram Alerts

1. Install:

```bash
pip install python-telegram-bot
```

2. Set **bot token** and **chat ID** in `utils.py` (or via environment variables)
3. Alerts sent for buy/sell signals or errors

---

## 🧭 System Architecture

```mermaid
graph LR
    A[Streamlit UI] -->|Tickers & Dates| B[Data Fetcher (yfinance)]
    B --> C[Indicators (pandas-ta)]
    C --> D[Signal Generator (RSI + SMA20/50)]
    C --> E[ML Features (MACD, OBV, MA diff, pct change)]
    E --> F[ML Model (RandomForest)]
    D --> G[Backtest + P&L (15-day exit)]
    G --> H[Google Sheets Logging]
    D --> I[Telegram Alerts]
    F --> A
    H --> A
```

---

## 🛠️ Troubleshooting

* **`ModuleNotFoundError: pandas_ta`** → `pip install pandas-ta`
* **Google auth errors** → Ensure `credentials.json` exists and matches service account
* **Empty yfinance data** → Verify ticker format (e.g., `RELIANCE.NS`) & date range
* **Telegram issues** → Ensure correct library (`python-telegram-bot`)

---

## 📅 Roadmap

* Parameterized RSI/SMA/exit horizon from UI
* Risk management (position sizing, stop-loss/take-profit)
* More strategies (MACD, Bollinger Bands, mean reversion)
* Portfolio-level metrics & equity curve
* Live trading integration (Zerodha/Upstox)
* Docker containerization
* Unit tests

---

## ⚠️ Disclaimer

**Educational use only.** Not financial advice. Past performance does not guarantee future returns.

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

```

---

If you want, I can **add GitHub badges** (Python version, Streamlit, License, Stars, etc.) at the top to make it look more professional.  
Do you want me to add those badges?
```
