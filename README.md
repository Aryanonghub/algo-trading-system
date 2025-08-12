Algorithmic Trading System (Python + Streamlit + ML)
A prototype algorithmic trading system that:

Fetches equity data (NIFTY 50 tickers via yfinance)

Generates trading signals using technical indicators (RSI + SMA crossover)

Backtests and logs results to Google Sheets

Trains an ML model (RandomForest) to predict next-day price movement

Provides an interactive Streamlit dashboard for visual analysis

Badges:

Python >= 3.10

Streamlit

scikit-learn

pandas-ta

yfinance

gspread

Features
Automated data ingestion: Daily OHLCV with yfinance

Strategy engine: RSI + SMA(20/50) crossover buy logic, 15-day exit assumption

ML predictions: RandomForest with RSI, MACD, OBV, volume, MA-diff, pct change

Google Sheets logging: Trade journal, P&L summary, win ratio tabs

Interactive UI: Streamlit dashboard for multi-ticker backtests and charts

Optional alerts: Telegram bot notifications for signals/errors

System Architecture
graph LR
    A[User/UI (Streamlit)] -->|configure tickers & dates| B[Data Fetcher (yfinance)]
    B --> C[Indicators (pandas-ta)]
    C --> D[Signal Generator (RSI + SMA20/50 crossover)]
    C --> E[ML Features (MACD, OBV, ma_diff, pct_change)]
    E --> F[ML Model (RandomForest)]
    D --> G[Backtest + P&L calc (15-day exit)]
    G --> H[Google Sheets (gspread)]
    D --> I[Telegram Alerts (optional)]
    F --> A
    H --> A

Tech Stack
Python, pandas, numpy

yfinance

pandas-ta

scikit-learn

Streamlit, Plotly

gspread, oauth2client

(Optional) python-telegram-bot

Project Structure
algo-trading-system/
├─ main.py           # Core pipeline: fetch → indicators → signals → ML → Sheets
├─ ui.py             # Streamlit dashboard
├─ strategy.py       # RSI + SMA(20/50) strategy and signal generation
├─ ml_model.py       # Feature engineering + RandomForest training/eval
├─ sheets.py         # Google Sheets auth + writing trades/P&L
├─ utils.py          # Logging + Telegram alert helper
├─ requirements.txt  # Python dependencies (see note below)
└─ credentials.json  # Google service account key (not committed)

Quick Start
1) Clone and enter the project

git clone https://github.com/Aryanonghub/algo-trading-system.git
cd algo-trading-system

2) Create and activate a virtual environment

python -m venv venv
# macOS/Linux: 
source venv/bin/activate
# Windows (PowerShell): 
.\venv\Scripts\Activate.ps1

3) Install dependencies
Note: requirements.txt currently needs a couple of fixes. Run:

pip install -r requirements.txt
pip install streamlit plotly pandas-ta python-telegram-bot

If you hit numpy conflicts, pin:

pip install "numpy==1.26.4"

4) Google Sheets setup (required)

Create a Google Cloud project

Enable: Google Drive API and Google Sheets API

Create a Service Account with Editor role

Generate a JSON key; save as credentials.json in the project root

Share your target Google Sheet with the service account email (Editor access)

Usage
Option A — Interactive Dashboard (recommended)

streamlit run ui.py

In the sidebar: select NIFTY 50 tickers, choose date range, click “Run Analysis”

Option B — CLI Backtesting Pipeline

python main.py

Uses defaults in main.py; logs to Google Sheets and algo_trading.log

Configuration Tips
Tickers: Edit nifty50_tickers in main.py; UI contains a curated set in ui.py

Date range: Set via Streamlit or adjust start/end in main.py

Exit rule horizon: In sheets.py the example P&L uses a 15-trading-day sell; change if needed

Sheet names/tabs: Update target sheet and worksheet titles in sheets.py

Logging: Outputs to algo_trading.log and console (see utils.setup_logging)

Google Sheets Output
Trades/Signals: Dated entries with buy events and prices

P&L Summary: Aggregated performance

Win Ratio: Strategy win percentage

Telegram Alerts (optional)
Install: pip install python-telegram-bot

Set your bot token and chat ID in utils.py (replace placeholders)

Or refactor to read from environment variables for production use

Troubleshooting
ModuleNotFoundError: pandas_ta:

pip install pandas-ta

Google auth errors:

Ensure credentials.json exists and matches the service account; the Sheet is shared with that service account email

Empty yfinance data:

Verify ticker symbols (e.g., RELIANCE.NS), date range, and network connectivity

Telegram import mismatch:

This code uses import telegram (python-telegram-bot). If you prefer pyTelegramBotAPI, adapt utils.py accordingly

requirements.txt oddities:

If you see “plotly yfinance” on one line or duplicate yfinance, install packages explicitly as listed above

Roadmap
Parameterization for RSI/SMA/exit horizon from UI

Risk management: position sizing, stop-loss/take-profit

Portfolio-level metrics and equity curve

Strategy library (e.g., MACD, Bollinger Bands, mean reversion)

Live trading bridge (e.g., Zerodha/Upstox) with paper/live toggle

Dockerfile and CI checks

Unit tests for strategy and sheet utilities

Contributing
Fork the repo

Create a feature branch: git checkout -b feat/your-feature

Commit changes: git commit -m "Add your feature"

Push and open a PR

License
No license file currently. Consider adding a LICENSE (e.g., MIT) for clarity.

Disclaimer
Educational prototype. Not investment advice. Use at your own risk. Past performance does not guarantee future results.