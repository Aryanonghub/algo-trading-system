# Algorithmic Trading System with ML and Automation

This project is a Python-based prototype of an algorithmic trading system. It automatically fetches stock data for NIFTY 50 stocks, backtests a trading strategy, logs performance to Google Sheets, and uses a machine learning model to predict future price movements.

-----

## Implemented Trading Strategy

This system generates a **BUY** signal based on a technical indicator pattern.

**Current Implementation Note:** For testing and demonstration purposes, the strategy in this version is configured to generate a signal based on a single condition:

  * **Golden Cross Condition**: A signal is generated whenever the 20-Day Moving Average (20-DMA) crosses **above** the 50-Day Moving Average (50-DMA).

The original, stricter two-part strategy (which also required an RSI \< 30) is currently bypassed to ensure that trade signals are generated, allowing for a full test of the system's logging and P\&L calculation capabilities.

The backtest calculates Profit & Loss by assuming a sale 15 trading days after the buy signal.

-----

## Core Features

  - 📈 **Automated Data Ingestion**: Fetches daily stock data for specified NIFTY 50 stocks using the `yfinance` API.
  - 🧠 **Trading Strategy Engine**: Implements and backtests the Golden Cross trading strategy.
  - 📊 **Google Sheets Integration**: Automatically logs a detailed trade journal, a summary of Profit & Loss (P\&L), and the strategy's win ratio to designated tabs in a Google Sheet.
  - 🤖 **Machine Learning Predictions**: Utilizes a Random Forest model with feature engineering to predict next-day price movement and reports its accuracy.
  - 📢 **Alerting Framework**: Includes an optional Telegram bot integration for sending trade signals and error notifications.

-----

## Project Structure

```
/algo_trading_project
├── main.py             # Main script to orchestrate the entire system
├── strategy.py         # Contains the trading logic and signal generation
├── ml_model.py         # ML model for price prediction and accuracy evaluation
├── sheets.py           # Handles all Google Sheets integration
├── utils.py            # Helper functions for logging and Telegram alerts
├── credentials.json    # (Required) Google API service account key
└── requirements.txt    # List of all Python dependencies
```

-----

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1\. Clone the Repository

```bash
git clone <your-repository-url>
cd algo_trading_project
```

### 2\. Create and Activate a Virtual Environment

```bash
# Create the environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Google API Setup (Crucial Step)

1.  Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable the **Google Drive API** and the **Google Sheets API**.
3.  Create a Service Account, grant it the **Editor** role, and download its JSON key.
4.  Rename the downloaded file to **`credentials.json`** and place it in the project root.
5.  Create a new Google Sheet and share it with the `client_email` found inside your `credentials.json` file.

-----

## How to Run

With the setup complete and the virtual environment active, run the main script from your terminal:

```bash
python main.py
```

The script will then execute the entire pipeline automatically, and the results will be populated in your Google Sheet.