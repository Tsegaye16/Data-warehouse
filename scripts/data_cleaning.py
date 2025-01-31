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

    def clean_text(self):
        """
        Clean the text by removing newlines, extra spaces, and extracting emojis.
        """
        if 'text' not in self.df.columns:
            logging.warning("Column 'text' not found in DataFrame. Skipping text cleaning.")
            return self.df
        
        self.df['text'] = self.df['text'].str.replace(r'\n', ' ', regex=True).str.strip()
        logging.info("Newlines removed and text trimmed in 'text' column.")
        
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
        self.df['emoji'] = self.df['text'].apply(lambda x: self._get_emojis(x) if isinstance(x, str) else 'no emoji')
        self.df['text'] = self.df['text'].apply(lambda x: ''.join([char for char in x if char not in emoji.EMOJI_DATA]) if isinstance(x, str) else x)
        logging.info("Extracted emojis and cleaned 'text' column of emojis.")

    def extract_links(self):
        """
        Extract YouTube links, website URLs, and phone numbers from the 'text' column.
        """
        if 'text' not in self.df.columns:
            logging.warning("Column 'text' not found in DataFrame. Skipping link extraction.")
            return self.df
        
        self.df['youtube'] = self.df['text'].apply(self._extract_youtube_links)
        self.df['website'] = self.df['text'].apply(self._extract_websites)
        self.df['phone'] = self.df['text'].apply(self._extract_phone_numbers)
        
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
        phone_pattern = r'\b(251|09)\d{8}\b'
        phone = re.findall(phone_pattern, text)
        return phone if phone else "no phone"

    def remove_duplicates(self):
        """
        Remove duplicate rows by converting lists to tuples (hashable type).
        """
        initial_shape = self.df.shape
        self.df = self.df.applymap(lambda x: tuple(x) if isinstance(x, list) else x)
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