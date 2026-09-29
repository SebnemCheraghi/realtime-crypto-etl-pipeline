import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message: str) -> bool:
        """
       Sending a text message to a Telegram bot
        """
        if not self.token or not self.chat_id:
            logger.warning("The Telegram token or chat ID has not been set in the environment variables.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("The message was successfully sent to Telegram.")
            return True
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            return False

# Local Test Sample
if __name__ == "__main__":
    notifier = TelegramNotifier()
   # notifier.send_message("Exchange Rate ETL Project Alarm System Test 🚀")