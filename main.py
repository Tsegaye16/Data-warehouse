import json
import os
import logging
from scripts.telegram_scrapper import TelegramScraper

os.makedirs("logs", exist_ok=True)
# Configure logging
logging.basicConfig(
    filename="logs/fetcher.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_metadata(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_metadata(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fetch_data(scraper, channels, metadata_file, raw_data_folder):
    metadata = load_metadata(metadata_file)
    os.makedirs(raw_data_folder, exist_ok=True)

    for channel in channels:
        logging.info(f"Fetching messages from {channel}...")
        last_fetched_id = metadata.get(channel, {}).get("last_fetched_id")

        try:
            messages = scraper.fetch_messages(channel, limit=200, min_id=last_fetched_id)
            if messages:
                file_name = os.path.join(raw_data_folder, f"{channel[1:]}.json")
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=4)
                    logging.info(f"Messages from {channel} saved to '{file_name}'.")

                metadata[channel] = {
                    "last_fetched_id": messages[0]["id"],  
                    "last_fetched_time": messages[0]["timestamp"]
                }
            else:
                logging.info(f"No new messages found for {channel}.")

        except Exception as e:
            logging.error(f"Error while fetching data from {channel}: {e}")

    save_metadata(metadata_file, metadata)
    logging.info("Metadata updated successfully.")

def main():
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
        fetch_data(scraper, channels, metadata_fetch_file, raw_data_folder)
    except Exception as e:
        logging.error(f"An error occurred during data fetching: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
