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
        self.create_table("raw_message")
    
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

    def create_table(self, table_name):
        """Create tables with relationships."""
        create_table_query = None
        if table_name == "raw_message":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                channel_name TEXT,
                message_id BIGINT UNIQUE,
                sender TEXT,
                timestamp TIMESTAMP,
                message TEXT,
                media TEXT,
                is_processed BOOLEAN DEFAULT FALSE
            );
            """
        elif table_name == "telegram_messages":
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                channel_title TEXT,
                message_id BIGINT UNIQUE REFERENCES raw_message(message_id) ON DELETE CASCADE,
                message TEXT,
                message_date TIMESTAMP,
                media_path TEXT,
                emoji TEXT,
                youtube TEXT,
                phone TEXT
            );
            """

        if create_table_query:
            try:
                with self.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                    connection.execute(text(create_table_query))
                logging.info(f"✅ Table '{table_name}' created successfully.")
            except Exception as e:
                logging.error(f"❌ Error creating table '{table_name}': {e}")
                raise


    def insert_data(self, cleaned_df, table_name):
        """Insert data and update processing status."""
        try:
            if table_name == "telegram_messages":
                cleaned_df["message_date"] = cleaned_df["message_date"].apply(lambda x: None if pd.isna(x) else str(x))

                insert_query = f"""
                INSERT INTO {table_name} 
                (channel_title, message_id, message, message_date, media_path, emoji, youtube, phone) 
                VALUES (:channel_title, :message_id, :message, :message_date, :media_path, :emoji, :youtube, :phone)
                ON CONFLICT (message_id) DO NOTHING;
                """

                update_query = f"""
                UPDATE raw_message SET is_processed = TRUE WHERE message_id = :message_id;
                """

                with self.engine.begin() as connection:
                    for _, row in cleaned_df.iterrows():
                        logging.info(f"Inserting: {row['message_id']} - {row['message_date']}")
                        connection.execute(
                            text(insert_query),
                            {
                                "channel_title": row["channel_title"],
                                "message_id": row["message_id"],
                                "message": row["message"],
                                "message_date": row["message_date"],
                                "media_path": row["media_path"],
                                "emoji": row["emoji"],
                                "youtube": row["youtube"],
                                "phone": row["phone"]
                            }
                        )
                        connection.execute(text(update_query), {"message_id": row["message_id"]})

                logging.info(f"✅ {len(cleaned_df)} records inserted into PostgreSQL and marked as processed.")

            elif table_name == "raw_message":
                insert_query = f""" 
                INSERT INTO {table_name} (channel_name, message_id, sender, timestamp, message, media) 
                VALUES (:channel_name, :message_id, :sender, :timestamp, :message, :media)
                ON CONFLICT (message_id) DO NOTHING; 
                """
                with self.engine.begin() as connection:
                    for _, row in cleaned_df.iterrows():
                        logging.info(f"Inserting: {row['id']} - {row['timestamp']}")
                        connection.execute(
                            text(insert_query),
                            {
                                "channel_name": row["name"],
                                "message_id": row["id"],
                                "sender": row["sender"],
                                "timestamp": row["timestamp"],
                                "message": row["text"],
                                "media": row["media"]
                            }
                        )

                logging.info(f"✅ {len(cleaned_df)} records inserted into raw_message.")

        except Exception as e:
            logging.error(f"❌ Error inserting data: {e}")
            raise

