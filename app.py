import json
import os
import logging
import re
from scripts.telegram_scrapper import TelegramScraper

os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/fetcher.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def load_metadata(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()  # Remove any leading/trailing spaces or newlines
                if not content:
                    return {}  # Return empty dictionary if the file is empty
                return json.loads(content)  # Parse JSON safely
        except json.JSONDecodeError as e:
            logging.error(f"Error loading metadata file '{file_path}': {e}")
            return {}  # Return empty dictionary if JSON is corrupted
    return {}  # If file doesn't exist, return empty metadata


async def save_metadata(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def fetch_data(scraper, channels, metadata_file, raw_data_folder):
    metadata = await load_metadata(metadata_file)
    os.makedirs(raw_data_folder, exist_ok=True)
    
    all_messages = []  # Store all fetched messages

    for channel in channels:
        logging.info(f"Fetching messages from {channel}...")
        last_fetched_id = metadata.get(channel, {}).get("last_fetched_id")

        try:
            messages = await scraper.fetch_messages(channel, limit=200, min_id=last_fetched_id)
            if messages:
                # Sanitize the channel name to create a valid file name
                sanitized_channel_name = re.sub(r'[^a-zA-Z0-9_]', '_', channel)
                file_name = os.path.join(raw_data_folder, f"{sanitized_channel_name}.json")
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=4)
                    logging.info(f"Messages from {channel} saved to '{file_name}'.")

                metadata[channel] = {
                    "last_fetched_id": messages[0]["id"],
                    "last_fetched_time": messages[0]["timestamp"]
                }

                all_messages.extend(messages)  # Append messages to all_messages list

            else:
                logging.info(f"No new messages found for {channel}.")

        except Exception as e:
            logging.error(f"Error while fetching data from {channel}: {e}")

    await save_metadata(metadata_file, metadata)
    logging.info("Metadata updated successfully.")

    return all_messages  # Return merged messages

async def mains():
    raw_data_folder = "data/raw"
    metadata_fetch_file = "metadata/last_fetched.json"
    os.makedirs("metadata", exist_ok=True)

    channels = [
        "https://t.me/DoctorsET",
        "https://t.me/CheMed123",
        "https://t.me/lobelia4cosmetics",
        "https://t.me/yetenaweg",
        "https://t.me/EAHCI"
    ]
    scraper = TelegramScraper()

    try:
        await scraper.start()  # Ensure the client is started
        all_fetched_messages = await fetch_data(scraper, channels, metadata_fetch_file, raw_data_folder)
        
        # Save merged data
        with open("data/merged_messages.json", "w", encoding="utf-8") as f:
            json.dump(all_fetched_messages, f, ensure_ascii=False, indent=4)
            logging.info(f"Merged messages saved to 'data/merged_messages.json'.")

        message = "Data fetching completed successfully." if all_fetched_messages else "No new messages found."

        return {"status": "success", "message": message, "data": all_fetched_messages}

    except Exception as e:
        logging.error(f"An error occurred during data fetching: {e}")
        return {"status": "error", "message": str(e), "data": []}

    finally:
        await scraper.close()

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(mains())
    print(json.dumps(result, indent=4, ensure_ascii=False))  # Print the result
