import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import pandas as pd
import time


def authorize_sheets(credentials_file='credentials.json'):
    """Authorizes and returns a gspread client object."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, scope)
        client = gspread.authorize(creds)
        logging.info("Successfully authorized Google Sheets client.")
        return client
    except Exception as e:
        logging.error(f"Failed to authorize Google Sheets: {e}")
        return None


def get_or_create_worksheet(spreadsheet, title):
    """Gets a worksheet by title, creating it if it doesn't exist."""
    try:
        worksheet = spreadsheet.worksheet(title)
        return worksheet
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=title, rows="1000", cols="20")
        return worksheet


def log_trades_to_sheet(client, sheet_name, signals_df):
    """
    Logs trade signals and backtest summary to a Google Sheet.
    """
    try:
        spreadsheet = client.open(sheet_name)

        # --- P&L Calculation Step with DEBUGGING ---
        print(f"--- DEBUG: Data received. Rows: {len(signals_df)} ---")

        signals_df['Sell_Price'] = signals_df.apply(
            lambda row: get_sell_price(row['Ticker'], row['Date']), axis=1)

        print("--- DEBUG: Sell prices calculated. Now dropping rows with no sell price...")

        # This is the critical step to check
        signals_df.dropna(subset=['Sell_Price'], inplace=True)

        print(
            f"--- DEBUG: Data after dropping rows. Remaining rows: {len(signals_df)} ---")

        if signals_df.empty:
            print(
                "--- DEBUG: PROBLEM CONFIRMED. The DataFrame is empty. Nothing will be uploaded. ---")
            logging.warning(
                "No valid trades with sell prices found. Sheet will not be updated.")
            return  # Stop the function here

        signals_df['P&L'] = signals_df['Sell_Price'] - signals_df['Price']

        # --- Data Upload Step ---
        trade_log_ws = get_or_create_worksheet(spreadsheet, "Trade Log")
        upload_df = signals_df.astype(str)
        trade_log_ws.clear()
        trade_log_ws.update(
            [upload_df.columns.values.tolist()] + upload_df.values.tolist())
        logging.info("Successfully logged trades to 'Trade Log' tab.")

        # --- Summary Calculation and Upload Step ---
        # (The rest of the function is the same)
        total_pnl = signals_df['P&L'].sum()
        pnl_summary_ws = get_or_create_worksheet(spreadsheet, "Summary P&L")
        pnl_summary_ws.clear()
        pnl_summary_ws.update(
            [['Metric', 'Value'], ['Total P&L', f'{total_pnl:.2f}']])
        logging.info("Successfully updated 'Summary P&L' tab.")

        wins = signals_df[signals_df['P&L'] > 0].shape[0]
        losses = signals_df[signals_df['P&L'] <= 0].shape[0]
        total_trades = wins + losses
        win_ratio = (wins / total_trades) * 100 if total_trades > 0 else 0
        win_ratio_ws = get_or_create_worksheet(spreadsheet, "Win Ratio")
        win_ratio_ws.clear()
        win_ratio_ws.update([['Metric', 'Value'], ['Total Trades', total_trades], [
                            'Winning Trades', wins], ['Win Ratio (%)', f'{win_ratio:.2f}']])
        logging.info("Successfully updated 'Win Ratio' tab.")

    except Exception as e:
        logging.error(f"An error occurred while writing to Google Sheets: {e}")


def get_sell_price(ticker, buy_date):
    """Helper function to get the closing price 15 days after the buy date."""
    try:
        time.sleep(0.5)
        import yfinance as yf
        sell_date = buy_date + pd.Timedelta(days=25)
        stock_data = yf.download(
            ticker, start=buy_date + pd.Timedelta(days=1), end=sell_date, progress=False)

        if stock_data.empty:
            return None

        for date, row in stock_data.iterrows():
            if (date - buy_date).days >= 15:
                return float(row['Close'])

        return None
    except Exception as e:
        logging.warning(
            f"Could not retrieve sell price for {ticker} on {buy_date.date()}: {e}")
        return None
