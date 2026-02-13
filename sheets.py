import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import pandas as pd
import yfinance as yf


# --------------------------------------
# GOOGLE SHEETS AUTHORIZATION
# --------------------------------------
def authorize_sheets(credentials_file="credentials.json"):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, scope
        )
        client = gspread.authorize(creds)
        logging.info("Google Sheets authorized successfully.")
        return client

    except Exception as e:
        logging.error(f"Google Sheets authorization failed: {e}")
        return None


# --------------------------------------
# GET OR CREATE WORKSHEET
# --------------------------------------
def get_or_create_worksheet(spreadsheet, title):
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows="1000", cols="20")


# --------------------------------------
# GET SELL PRICE (FIXED VERSION)
# --------------------------------------
def get_sell_price(ticker, buy_date):
    """
    Returns closing price at least 15 trading days after buy_date.
    """
    try:
        buy_date = pd.to_datetime(buy_date)

        future_data = yf.download(
            ticker,
            start=buy_date,
            end=buy_date + pd.Timedelta(days=40),
            progress=False
        )

        if future_data.empty:
            return None

        future_data = future_data.reset_index()
        future_data["Days_After"] = (
            future_data["Date"] - buy_date).dt.days

        valid_rows = future_data[future_data["Days_After"] >= 15]

        if valid_rows.empty:
            return None

        return float(valid_rows.iloc[0]["Close"])

    except Exception as e:
        logging.warning(
            f"Sell price retrieval failed for {ticker} on {buy_date}: {e}")
        return None


# --------------------------------------
# MAIN FUNCTION TO LOG TRADES
# --------------------------------------
def log_trades_to_sheet(client, sheet_name, signals_df):
    try:
        spreadsheet = client.open(sheet_name)

        if signals_df.empty:
            logging.warning("Signals DataFrame is empty.")
            return

        # Ensure Date column is datetime
        signals_df["Date"] = pd.to_datetime(signals_df["Date"])

        print(f"Processing {len(signals_df)} trades...")

        # Calculate sell prices
        signals_df["Sell_Price"] = signals_df.apply(
            lambda row: get_sell_price(row["Ticker"], row["Date"]),
            axis=1
        )

        print("Sell prices calculated.")

        # Remove rows with no sell price
        signals_df = signals_df.dropna(subset=["Sell_Price"])

        if signals_df.empty:
            logging.warning("No valid sell prices found.")
            print("No valid trades found after sell price calculation.")
            return

        # Calculate P&L
        signals_df["P&L"] = (
            signals_df["Sell_Price"] - signals_df["Price"]
        )

        # --------------------------------------
        # Upload Trade Log
        # --------------------------------------
        trade_ws = get_or_create_worksheet(spreadsheet, "Trade Log")
        trade_ws.clear()

        upload_df = signals_df.astype(str)

        trade_ws.update(
            [upload_df.columns.values.tolist()] +
            upload_df.values.tolist()
        )

        logging.info("Trade Log updated successfully.")

        # --------------------------------------
        # Upload Summary P&L
        # --------------------------------------
        total_pnl = signals_df["P&L"].sum()

        summary_ws = get_or_create_worksheet(spreadsheet, "Summary P&L")
        summary_ws.clear()

        summary_ws.update([
            ["Metric", "Value"],
            ["Total P&L", f"{total_pnl:.2f}"]
        ])

        logging.info("Summary P&L updated successfully.")

        # --------------------------------------
        # Upload Win Ratio
        # --------------------------------------
        wins = signals_df[signals_df["P&L"] > 0].shape[0]
        losses = signals_df[signals_df["P&L"] <= 0].shape[0]
        total_trades = wins + losses

        win_ratio = (
            (wins / total_trades) * 100
            if total_trades > 0 else 0
        )

        win_ws = get_or_create_worksheet(spreadsheet, "Win Ratio")
        win_ws.clear()

        win_ws.update([
            ["Metric", "Value"],
            ["Total Trades", total_trades],
            ["Winning Trades", wins],
            ["Losing Trades", losses],
            ["Win Ratio (%)", f"{win_ratio:.2f}"]
        ])

        logging.info("Win Ratio updated successfully.")

        print("Google Sheets updated successfully.")

    except Exception as e:
        logging.error(
            f"Error while logging trades to Google Sheets: {e}")
        print(f"Error: {e}")
