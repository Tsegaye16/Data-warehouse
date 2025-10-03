import logging
from telethon.sync import TelegramClient
from telethon import functions, types
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()



class TelegramScraper:
    def __init__(self, session_name='scraper_session'):
        
        self.session_name = session_name
        self.client = TelegramClient(session_name, os.getenv("API_ID"), os.getenv("API_HASH"))
        self.is_authenticated = False

    async def start(self):
        await self.client.start()
        
        self.is_authenticated = True

    async def authenticate(self, phone, password=None, code=None):
        """Authenticate with Telegram"""
        try:
            await self.client.connect()
            
            # Send code request
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(phone)
                # logging.info(f"Authentication code sent to {phone}")
                
                if code:
                    # Sign in with code
                    await self.client.sign_in(phone, code, password=password)
                    # logging.info("Successfully authenticated with code")
                else:
                    return {"status": "code_required", "message": "Authentication code required"}
            
            self.is_authenticated = True
            return {"status": "success", "message": "Authenticated successfully"}
            
        except Exception as e:
            # logging.error(f"Authentication error: {e}")
            return {"status": "error", "message": str(e)}

    async def check_authentication(self):
        """Check if the client is authenticated"""
        try:
            if await self.client.is_user_authorized():
                self.is_authenticated = True
                return True
            return False
        except:
            return False

    async def fetch_messages(self, channel_name, limit=100, min_id=None):
        if not self.is_authenticated:
            raise Exception("Client not authenticated. Please authenticate first.")

        if min_id is None:
            min_id = 0

        messages = []
        try:
            # logging.info(f"Fetching messages from {channel_name} with min_id={min_id}...")
            async for message in self.client.iter_messages(channel_name, limit=limit, min_id=min_id):
                msg_data = {
                    "id": message.id,
                    "channel_name": message.chat.title if message.chat else "Unknown",
                    "sender": message.sender_id,
                    "timestamp": message.date.isoformat(),
                    "text": message.message or "",
                    "media": "No media",
                }
                messages.append(msg_data)
            # logging.info(f"Fetched {len(messages)} messages from {channel_name}.")
        except Exception as e:
            # logging.error(f"Error fetching messages from {channel_name}: {e}")
            pass
        return messages

    async def close(self):
        # logging.info("Disconnecting Telegram client...")
        await self.client.disconnect()
        # logging.info("Telegram client disconnected.")