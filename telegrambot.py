"""
telegrambot.py

This file connects the trading pipeline to Telegram.

Flow:
1. User runs /start
2. Bot shows stock selection buttons
3. User selects a stock
4. Bot fetches 365-day data
5. Bot displays:
   - Stock summary (price stats)
   - Total crossover count
   - Detailed crossover events
"""

import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from main import run_trading_pipeline


# =====================================================
# CONFIGURATION
# =====================================================

# BOT_TOKEN should be stored securely as an environment variable.
# Example (Mac/Linux terminal):
# export BOT_TOKEN="your_real_token_here"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# List of available stocks shown as inline buttons.
AVAILABLE_STOCKS = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "MARUTI.NS",
    "INFY.NS",
    "TCS.NS",
    "ICICIBANK.NS"
]


# =====================================================
# HELPER FUNCTION
# =====================================================

def send_message(chat_id, message):
    """
    Centralized function to send messages.
    Keeps sending logic in one place for easier modification later.
    """
    bot.send_message(chat_id, message)


# =====================================================
# START COMMAND HANDLER
# =====================================================

@bot.message_handler(commands=["start"])
def start(message):
    """
    Triggered when user types /start.

    Displays an inline keyboard with available stocks.
    """

    markup = InlineKeyboardMarkup()

    # Dynamically create one button per stock
    for stock in AVAILABLE_STOCKS:
        markup.add(
            InlineKeyboardButton(
                text=stock,
                callback_data=stock
            )
        )

    bot.send_message(
        message.chat.id,
        "📈 Select a stock to scan (Last 365 Days Data):",
        reply_markup=markup
    )


# =====================================================
# STOCK SELECTION HANDLER
# =====================================================

@bot.callback_query_handler(func=lambda call: call.data in AVAILABLE_STOCKS)
def handle_stock_selection(call):
    """
    Triggered when a user clicks one of the stock buttons.

    Steps:
    1. Fetch stock data via run_trading_pipeline()
    2. Display summary statistics
    3. Display crossover details
    """

    chat_id = call.message.chat.id
    ticker = call.data

    # Acknowledge button click (removes loading animation in Telegram)
    bot.answer_callback_query(call.id)

    send_message(chat_id, f"⏳ Fetching 365 days data for {ticker}...")

    # Run main trading logic
    result = run_trading_pipeline(ticker)

    total_crossovers = result["total_crossovers"]
    summary = result["summary"]
    all_crossovers = result.get("last_5_crossovers", [])

    # If no summary returned, something went wrong
    if summary is None:
        send_message(chat_id, "❌ Could not fetch stock data.")
        return

    # =====================================================
    # STOCK SUMMARY SECTION
    # =====================================================

    summary_message = (
        f"📊 Stock Summary (Last {summary['data_period_days']} Days)\n\n"
        f"Current Price: ₹{summary['current_price']:.2f}\n"
        f"Highest Price: ₹{summary['highest_price']:.2f}\n"
        f"Lowest Price: ₹{summary['lowest_price']:.2f}\n\n"
        f"🔁 Total Crossovers Found: {total_crossovers}"
    )

    send_message(chat_id, summary_message)

    # =====================================================
    # CROSSOVER DETAILS SECTION
    # =====================================================

    # If no crossover events were detected
    if total_crossovers == 0:
        send_message(chat_id, "No crossover events found.")
        return

    send_message(chat_id, "\n📌 Crossover Events:")

    # Display each crossover event
    for row in all_crossovers:

        detail = (
            f"\n• Date: {row['Date']}\n"
            f"  Signal: {row['Signal']}\n"
            f"  Price: ₹{row['Price']:.2f}"
        )

        send_message(chat_id, detail)


# =====================================================
# FALLBACK HANDLER
# =====================================================

@bot.message_handler(func=lambda message: True)
def fallback(message):
    """
    Handles any message that doesn't match known commands.

    Keeps user flow controlled.
    """
    send_message(
        message.chat.id,
        "Type /start to select a stock."
    )


# =====================================================
# BOT ENTRY POINT
# =====================================================

if __name__ == "__main__":
    """
    Starts the Telegram bot using long polling.
    skip_pending=True prevents processing old queued messages.
    """
    print("🤖 Telegram Bot is running...")
    bot.infinity_polling(skip_pending=True)
