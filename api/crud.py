from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import os,sys
from typing import Optional

from models import TelegramMessage,RawTelegramMessage
import schemas

sys.path.append(os.path.abspath(os.path.join('..', 'scripts')))

from data_cleaning import DataFrameCleaner


def get_telegram_messages(db: Session, skip: int = 0, limit: int = 10, channel_title: Optional[str] = None):
    """
    Retrieve messages with pagination support.
    :param db: Database session
    :param skip: Number of records to skip (for pagination)
    :param limit: Number of records to return (page size)
    :param channel_title: Filter messages by channel title (optional)
    :return: List of messages and total count
    """
    # Base query
    query = db.query(TelegramMessage)
    if channel_title:
        query = query.filter(TelegramMessage.channel_title.ilike(f"%{channel_title}%"))

    messages = query.offset(skip).limit(limit).all()

    # Get the total count of messages
    total = query.count()  # Corrected total count calculation

    return messages, total


def get_raw_telegram_message(
    db: Session,
    skip: int = 0,
    limit: int = 0,
    channel_name: Optional[str] = None 
):
    # Base query
    query = db.query(RawTelegramMessage).filter(RawTelegramMessage.is_processed == False)

    # Apply channel_name filter if provided
    if channel_name:
        query = query.filter(RawTelegramMessage.channel_name.ilike(f"%{channel_name}%"))  # Case-insensitive search

    # Apply pagination
    messages = query.offset(skip).limit(limit).all()

    # Get total count (with the same filters applied)
    total_query = db.query(func.count(RawTelegramMessage.id)).filter(RawTelegramMessage.is_processed == False)
    if channel_name:
        total_query = total_query.filter(RawTelegramMessage.channel_name.ilike(f"%{channel_name}%"))
    total = total_query.scalar()

    return messages, total

def insert_raw_messages(db: Session, messages: list[dict]):
    """
    Insert new messages into the raw_message table.
    :param db: Database session
    :param messages: List of messages (dict format)
    :return: Tuple of (list of new messages, total number of new messages inserted)
    """
    new_messages = []  # Track all newly inserted messages
    for msg in messages:
        # Check if the message already exists (based on message_id)
        existing_msg = db.query(RawTelegramMessage).filter_by(message_id=msg["id"]).first()
        if not existing_msg:
            new_msg = RawTelegramMessage(
                channel_name=msg.get("channel_name") if msg.get("channel_name") else "No channel name",
                message_id=msg.get("id") if msg.get("id") else "no message id",
                sender=msg.get("sender") if msg.get("sender") else "No sender",
                timestamp=msg.get("timestamp") if msg.get("timestamp") else "No timestamp",
                message=msg.get("text") if msg.get("text") else "No message",
                media=msg.get("media") if msg.get("media") else "No media",
                is_processed=False  # New messages are not processed yet
            )
            db.add(new_msg)
            new_messages.append(new_msg)  # Add the new message to the list
    
    db.commit()  # Commit all new messages
    total = len(new_messages)  # Calculate the total number of new messages inserted
    return new_messages, total


def fetch_and_process_messages(db: Session):
    """
    Fetch raw messages, preprocess them, and insert into the telegram_messages table.
    """
    try:
        # Fetch raw messages excluding 'id' and 'is_processed' columns
        raw_messages = db.query(
            RawTelegramMessage.channel_name,
            RawTelegramMessage.message_id,
            RawTelegramMessage.sender,
            RawTelegramMessage.timestamp,
            RawTelegramMessage.message,
            RawTelegramMessage.media
        ).filter(RawTelegramMessage.is_processed == False).all()

        # Convert raw messages to a DataFrame
        df = pd.DataFrame([msg._asdict() for msg in raw_messages])
        print("Columns before preprocessing:", df.columns.to_list())

        # Apply preprocessing
        cleaner = DataFrameCleaner(df)
        cleaner.clean_text()
        cleaner.extract_links()
        cleaner.remove_duplicates()
        cleaner.convert_timestamp("timestamp")
        cleaner.clean_null_values()
        cleaner.restructure()

        print("Columns after preprocessing:", df.columns.to_list())

        # Insert cleaned data into the telegram_messages table
        for _, row in df.iterrows():
            new_message = TelegramMessage(
                channel_title=row["channel_name"],
                message_id=row["message_id"],
                message=row["message"],
                message_date=row["timestamp"],
                media_path=row["media"],
                emoji=row["emoji"],
                youtube=row["youtube"][0] if isinstance(row["youtube"], list) else row["youtube"],
                phone=row["phone"]
            )
            db.add(new_message)
           
        # Mark raw messages as processed
        db.query(RawTelegramMessage).filter(RawTelegramMessage.is_processed == False).update({"is_processed": True})
        db.commit()

        return {"status": "success", "message": f"{len(df)} messages processed and inserted into telegram_messages."}
    except Exception as e:
        db.rollback()
        raise e