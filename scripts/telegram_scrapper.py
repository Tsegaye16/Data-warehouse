import logging
from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.makedirs("logs", exist_ok=True)
# Configure logging
logging.basicConfig(
    filename="logs/scraper.log",  # Log file name
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = 'scraper_session'

class TelegramScraper:
    def __init__(self):
        logging.info("Initializing Telegram client...")
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    async def start(self):
        await self.client.start()
        logging.info("Telegram client started successfully.")

    async def fetch_messages(self, channel_name, limit=100, min_id=None):
        if min_id is None:
            min_id = 0

        messages = []
        try:
            logging.info(f"Fetching messages from {channel_name} with min_id={min_id}...")
            async for message in self.client.iter_messages(channel_name, limit=limit, min_id=min_id):
                msg_data = {
                    "id": message.id,
                    "channel_name": message.chat.title if message.chat else "Unknown",
                    "sender": message.sender_id,
                    "timestamp": message.date.isoformat(),
                    "text": message.message or "",
                    "media": "No media",  # Ignore media
                }
                messages.append(msg_data)
            logging.info(f"Fetched {len(messages)} messages from {channel_name}.")
        except Exception as e:
            logging.error(f"Error fetching messages from {channel_name}: {e}")

        return messages

    async def close(self):
        logging.info("Disconnecting Telegram client...")
        await self.client.disconnect()
        logging.info("Telegram client disconnected.")
