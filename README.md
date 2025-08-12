Algorithmic Trading System with ML and Interactive UI
This project is a complete prototype of an algorithmic trading system built in Python. It features a command-line backtesting engine and an interactive web-based dashboard built with Streamlit.

The system automatically fetches stock data, backtests a trading strategy based on technical indicators, logs performance to Google Sheets, and uses a machine learning model to predict future price movements.

Key Features
📈 Automated Data Ingestion: Fetches daily stock data for specified NIFTY 50 stocks using the yfinance API.

🧠 Trading Strategy Engine: Implements and backtests a trading strategy combining the Relative Strength Index (RSI) and a Moving Average Crossover (Golden Cross).

📊 Google Sheets Integration: Automatically logs a detailed trade journal, a summary of Profit & Loss (P&L), and the strategy's win ratio to designated tabs in a Google Sheet.

🤖 Machine Learning Predictions: Utilizes a Random Forest model with feature engineering (RSI, MACD, OBV, Volume) and hyperparameter tuning to predict next-day price movement and reports its accuracy.

🖥️ Interactive Streamlit Dashboard: A user-friendly web interface (ui.py) to visually run backtests, select stocks, set date ranges, and view results and charts in real-time.

📢 Alerting Framework: Includes an optional Telegram bot integration for sending trade signals and error notifications.

Project Structure
/algo_trading_project
├── main.py             # Core script to run the backtesting engine
├── ui.py               # Script to launch the interactive Streamlit UI
├── strategy.py         # Contains the trading logic and signal generation
├── ml_model.py         # ML model for price prediction and accuracy evaluation
├── sheets.py           # Handles all Google Sheets integration
├── utils.py            # Helper functions (logging, Telegram alerts)
├── credentials.json    # (Required) Google API service account key
└── requirements.txt    # List of all Python dependencies

How to Run the Project
You can run this project in two ways: through the command-line engine or the interactive web UI.

Option 1: Run the Interactive Dashboard (Recommended)
This is the easiest way to use the project.

streamlit run ui.py

Your web browser will automatically open a new tab with the dashboard, where you can configure and run your analysis visually.

Option 2: Run the Core Backtesting Engine
To run the automated backtesting script from your terminal:

python main.py

The script will run with the default parameters set in the file and log the results to Google Sheets.

Setup and Installation
Follow these steps to set up and run the project locally.

1. Clone the Repository
git clone <your-repository-url>
cd algo_trading_project

2. Create and Activate a Virtual Environment
# Create the environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

3. Install Dependencies
Install all required libraries, including Streamlit for the UI.

pip install -r requirements.txt
pip install streamlit plotly

Note: Ensure your requirements.txt specifies numpy==1.26.4 to avoid version conflicts.

4. Google API Setup (Crucial Step)
Create a Google Cloud Project: Go to the Google Cloud Console and create a new project.

Enable APIs: In your new project, enable the Google Drive API and the Google Sheets API.

Create a Service Account: Navigate to "IAM & Admin" > "Service Accounts", create a new service account, and grant it the Editor role.

Generate a JSON Key: Create a key for the new service account (Key type: JSON). A .json file will be downloaded.

Add Credentials to Project: Rename the downloaded file to credentials.json and place it in the project root.

Share Your Google Sheet: Create a new blank Google Sheet. Open the credentials.json file, copy the client_email address, and share your Google Sheet with that email, giving it Editor permissions.

Implemented Trading Strategy
The system generates a BUY signal when two conditions are met simultaneously for a stock:

Oversold Condition: The 14-day RSI drops below 30.

Bullish Confirmation: The 20-Day Moving Average (20-DMA) crosses above the 50-Day Moving Average (50-DMA).

The backtest calculates P&L by assuming a sale 15 trading days after the buy signal.

Machine Learning Model
Model: RandomForestClassifier is used to predict if the next day's closing price will be higher (1) or lower (0).

Features: The model is trained on a rich set of features, including RSI, MACD, On-Balance Volume (OBV), raw Trading Volume, and more.

Tuning: The script uses GridSearchCV to automatically find the best hyperparameters for the model to improve its predictive accuracy.
