import os,sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

os.makedirs("logs", exist_ok=True)
# Configure logging
logging.basicConfig(
    filename="../logs/database_setup.log",  # Log file name
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
class TelegramDBManager:
    def __init__(self):
        """Initialize the database manager by loading environment variables and setting up logging."""
      

       

        # Load environment variables
        load_dotenv("../.env")
        
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        
        
        self.engine = self.get_db_connection()
        self.create_table()
    
    def get_db_connection(self):
        """Create and return a database engine."""
        try:
            DATABASE_URL = self.DATABASE_URL
            engine = create_engine(DATABASE_URL)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))  # Test connection
            logging.info("✅ Successfully connected to the PostgreSQL database.")
            return engine
        except Exception as e:
            logging.error(f"❌ Database connection failed: {e}")
            raise

    def create_table(self):
        """Create the telegram_messages table if it does not exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS telegram_messages (
            id SERIAL PRIMARY KEY,
            channel_title TEXT,
            message_id BIGINT UNIQUE,
            message TEXT,
            message_date TIMESTAMP,
            media_path TEXT,
            emoji TEXT,       -- Column for extracted emojis
            youtube TEXT,     -- Column for extracted YouTube links
            phone TEXT      -- Column for extracted phone number
        );
        """
        try:
            with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                connection.execute(text(create_table_query))
            logging.info("✅ Table 'telegram_messages' created successfully.")
        except Exception as e:
            logging.error(f"❌ Error creating table: {e}")
            raise

    def insert_data(self, cleaned_df):
        """Insert cleaned Telegram data into the PostgreSQL database."""
        try:
            # Convert NaT timestamps to None (NULL in SQL)
            cleaned_df["message_date"] = cleaned_df["message_date"].apply(lambda x: None if pd.isna(x) else str(x))

            insert_query = """
            INSERT INTO telegram_messages 
            (channel_title, message_id, message, message_date, media_path, emoji, youtube, phone) 
            VALUES (:channel_title,  :message_id, :message, :message_date, :media_path, :emoji, :youtube, :phone)
            ON CONFLICT (message_id) DO NOTHING;
            """

            with self.engine.begin() as connection:  # ✅ Auto-commit enabled
                for _, row in cleaned_df.iterrows():
                    logging.info(f"Inserting: {row['message_id']} - {row['message_date']}")
                    connection.execute(
                        text(insert_query),
                        {
                            "channel_title": row["channel_title"],
                            "message_id": row["message_id"],
                            "message": row["message"],
                            "message_date": row["message_date"],  # ✅ No NaT values
                            "media_path": row["media_path"],
                            "emoji": row["emoji"],
                            "youtube": row["youtube"],
                            "phone":row["phone"]
                        }
                    )
            logging.info(f"✅ {len(cleaned_df)} records inserted into PostgreSQL database.")
        except Exception as e:
            logging.error(f"❌ Error inserting data: {e}")
            raise