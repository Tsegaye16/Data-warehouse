from datetime import datetime
import pandas as pd
import os
import logging
import re
import emoji

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="../logs/data_cleaning.log",  # Log file inside 'logs' folder
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class DataFrameCleaner:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a pandas DataFrame.
        """
        self.df = df
        logging.info("DataFrameCleaner initialized with DataFrame of shape %s", self.df.shape)

    def clean_text(self):
        """
        Clean the text by removing newlines, extra spaces, and extracting emojis.
        """
        if 'message' not in self.df.columns:
            raise ValueError("Column 'message' not found in DataFrame.")
        
        self.df['message'] = self.df['message'].str.replace(r'\n', ' ', regex=True).str.strip()
        logging.info("Newlines removed and text trimmed in 'message' column.")
        
        self._extract_emojis()
        logging.info("Emoji extraction completed.")
        return self.df

    def _get_emojis(self, text: str):
        """
        Extract emojis from a given text.
        """
        return ''.join([char for char in text if char in emoji.EMOJI_DATA])

    def _extract_emojis(self):
        """
        Extract emojis from text columns and store them in a new 'emoji' column.
        """
        self.df['emoji'] = self.df['message'].apply(lambda x: self._get_emojis(x) if isinstance(x, str) else 'no emoji')
        self.df['message'] = self.df['message'].apply(lambda x: ''.join([char for char in x if char not in emoji.EMOJI_DATA]) if isinstance(x, str) else x)
        logging.info("Extracted emojis and cleaned 'message' column of emojis.")

    def extract_links(self):
        """
        Extract YouTube links, website URLs, and phone numbers from the 'message' column.
        """
        if 'message' not in self.df.columns:
            raise ValueError("Column 'message' not found in DataFrame.")
        
        self.df['youtube'] = self.df['message'].apply(self._extract_youtube_links)
        self.df['website'] = self.df['message'].apply(self._extract_websites)
        self.df['phone'] = self.df['message'].apply(self._extract_phone_numbers)
        
        logging.info("Extracted YouTube links, website URLs, and phone numbers.")
        return self.df

    def _extract_youtube_links(self, text: str):
        youtube_pattern = r'(https?://(?:www\.)?youtube(?:-nocookie)?\.com/(?:[^ \n]+)?|https?://youtu\.be/[\w\-]+)'
        youtube = re.findall(youtube_pattern, text)
        return youtube if youtube else "no youtube"

    def _extract_websites(self, text: str):
        website_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
        website = re.findall(website_pattern, text)
        return website if website else "no website"

    def _extract_phone_numbers(self, text: str):
        patterns = [
            r'\+251\d{9}',  # Matches numbers starting with +251 followed by 9 digits
            r'09\d{8}',     # Matches numbers starting with 09 followed by 8 digits
            r'07\d{8}',     # Matches numbers starting with 07 followed by 8 digits
            r'\b\d{4}\b'    # Matches 4-digit short numbers
        ]
        combined_pattern = '|'.join(patterns)
        phone = re.findall(combined_pattern, text)
        return phone if phone else []

    def remove_duplicates(self):
        """
        Remove duplicate rows by converting lists to tuples (hashable type).
        """
        initial_shape = self.df.shape

        # Convert lists to tuples in all columns
        self.df = self.df.apply(lambda col: col.apply(lambda x: tuple(x) if isinstance(x, list) else x))

        # Drop duplicates
        self.df = self.df.drop_duplicates()
        final_shape = self.df.shape
        
        logging.info("Removed duplicates. Rows before: %d, Rows after: %d", initial_shape[0], final_shape[0])
        return self.df

    def convert_timestamp(self, column_name="timestamp"):
        """
        Convert timestamps from '2024-05-26 16:11:43+00:00' to '2023-12-18 17:04:02' format.
        """
        if column_name in self.df.columns:
            try:
                self.df[column_name] = self.df[column_name].apply(
                    lambda x: datetime.strptime(str(x).split('+')[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                    if isinstance(x, str) else x
                )
                logging.info(f"Timestamps in column '{column_name}' converted successfully.")
            except Exception as e:
                logging.error(f"Error converting timestamps in column '{column_name}': {e}")
        else:
            logging.warning(f"Column '{column_name}' not found in DataFrame.")
        return self.df

    def clean_null_values(self):
        """
        Replace NaN, None, and empty strings with 'no <column name>' in all columns.
        """
        for column in self.df.columns:
            null_mask = self.df[column].isna() | (self.df[column] == "") | (self.df[column].astype(str).str.lower() == "nan")
            null_count = null_mask.sum()
            
            if null_count > 0:
                self.df.loc[null_mask, column] = f'no {column}'
                logging.info("Replaced %d null values in column '%s' with 'no %s'.", null_count, column, column)
        
        logging.info("Null value cleaning completed. Current DataFrame shape: %s", self.df.shape)
        return self.df

    def restructure(self):
        """
        Rename columns to match the telegram_messages table schema.
        """
        self.df = self.df.rename(columns={
            "channel_name": "channel_title",
            "timestamp": "message_date",
            "message": "message",
            "media": "media_path"
        })
        return self.df 
