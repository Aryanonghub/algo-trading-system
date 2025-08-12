import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

# Import project modules
from utils import setup_logging, send_telegram_alert
from strategy import add_indicators, generate_signals
from sheets import authorize_sheets, log_trades_to_sheet, get_or_create_worksheet
from ml_model import train_ml_model, create_features


def run_trading_pipeline():
    """
    The main function to orchestrate the entire algo-trading process.
    """
    logger = setup_logging()
    logger.info("--- Starting Algo-Trading System ---")

    # --- 1. CONFIGURATION & DATA INGESTION ---
    nifty50_tickers = ['RELIANCE.NS', 'HDFCBANK.NS', 'MARUTI.NS']
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    logger.info(
        f"Fetching data for {nifty50_tickers} from {start_date.date()} to {end_date.date()}")
    try:
        data = yf.download(nifty50_tickers, start=start_date,
                           end=end_date, group_by='ticker')
        if data.empty:
            raise ValueError("No data downloaded from yfinance.")
    except Exception as e:
        logger.error(f"Failed to download stock data: {e}")
        return

    all_signals = []
    all_data_for_ml = []

    # --- 2. STRATEGY & FEATURE CALCULATION (PER TICKER) ---
    for ticker in nifty50_tickers:
        logger.info(f"Processing ticker: {ticker}")
        df = data[ticker].copy()
        df.dropna(inplace=True)
        if df.empty:
            continue

        df['Ticker'] = ticker
        df_with_indicators = add_indicators(df)
        df_with_ml_features = create_features(df_with_indicators)
        all_data_for_ml.append(df_with_ml_features)
        
        # --- Using the original, correct strategy ---
        signals = generate_signals(df_with_indicators) 
        if not signals.empty:
            all_signals.append(signals)
            logger.info(f"Found {len(signals)} signals for {ticker}.")
    
    # --- 3. GOOGLE SHEETS AUTOMATION (UPDATED LOGIC) ---
    gspread_client = authorize_sheets()
    if gspread_client:
        if all_signals:
            logger.info("Signals found. Logging trades to Google Sheets.")
            final_signals_df = pd.concat(all_signals, ignore_index=True)
            log_trades_to_sheet(gspread_client, 'AlgoTrading_Assignment_Log', final_signals_df)
            send_telegram_alert(f"Trade backtest complete. {len(final_signals_df)} signals logged to Google Sheets.")
        else:
            # --- THIS IS THE NEW FIX ---
            logger.info("No trade signals found. Clearing old data from Google Sheets.")
            try:
                spreadsheet = gspread_client.open('AlgoTrading_Assignment_Log')
                # Clear each sheet to reflect the "no signals" result
                get_or_create_worksheet(spreadsheet, "Trade Log").clear()
                get_or_create_worksheet(spreadsheet, "Summary P&L").clear()
                get_or_create_worksheet(spreadsheet, "Win Ratio").clear()
                # Optional: Add headers back to the empty sheets
                get_or_create_worksheet(spreadsheet, "Trade Log").append_row(["Date", "Stock", "Signal", "Price", "P&L"])
                get_or_create_worksheet(spreadsheet, "Summary P&L").append_row(["Metric", "Value"])
                get_or_create_worksheet(spreadsheet, "Win Ratio").append_row(["Metric", "Value"])
                logger.info("Successfully cleared sheets.")
            except Exception as e:
                logger.error(f"Failed to clear Google Sheets: {e}")
            send_telegram_alert("Trade backtest complete. No new signals were found.")

    # --- 4. ML AUTOMATION (BONUS) ---
    if all_data_for_ml:
        full_ml_data = pd.concat(all_data_for_ml)
        accuracy = train_ml_model(full_ml_data)
        send_telegram_alert(f"ML Model training complete. Prediction Accuracy: {accuracy:.2f}%")

    logger.info("--- Algo-Trading System Run Finished ---")


if __name__ == '__main__':
    run_trading_pipeline()