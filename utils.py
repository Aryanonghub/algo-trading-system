import logging
import telegram

# --- LOGGING SETUP ---


def setup_logging():
    """Configures the logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("algo_trading.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# --- TELEGRAM ALERT (BONUS) ---
# Add Telegram alert integration for signal alerts or error notifications.


def send_telegram_alert(message):
    """
    Sends a message to a predefined Telegram chat.
    Replace 'YOUR_BOT_TOKEN' and 'YOUR_CHAT_ID' with your actual credentials.
    """
    try:
        # !!! IMPORTANT: Replace with your actual Bot Token and Chat ID !!!
        bot_token = 'YOUR_BOT_TOKEN'
        chat_id = 'YOUR_CHAT_ID'

        if bot_token == 'YOUR_BOT_TOKEN' or chat_id == 'YOUR_CHAT_ID':
            logging.warning(
                "Telegram credentials are not set. Skipping alert.")
            return

        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message)
        logging.info(f"Successfully sent Telegram alert: {message}")
    except Exception as e:
        logging.error(f"Failed to send Telegram alert: {e}")
