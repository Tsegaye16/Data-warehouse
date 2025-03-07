from sqlalchemy.orm import Session
from sqlalchemy import func
from models import TelegramMessage,RawTelegramMessage
import schemas

def get_telegram_messages(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieve messages with pagination support.
    :param db: Database session
    :param skip: Number of records to skip (for pagination)
    :param limit: Number of records to return (page size)
    :return: List of messages and total count
    """
    # Query messages with pagination
    messages = db.query(TelegramMessage).offset(skip).limit(limit).all()
    # Get the total count of messages in the database
    total = db.query(func.count(TelegramMessage.id)).scalar()
    return messages, total

def get_raw_telegram_message(db:Session, skip:int = 0, limit:int = 0):
    # Query messages with pagination
    messages = db.query(RawTelegramMessage).filter(RawTelegramMessage.is_processed == False).offset(skip).limit(limit).all()
    total = db.query(func.count(RawTelegramMessage.id)).filter(RawTelegramMessage.is_processed == False).scalar()
    return messages, total


def add_raw_telegram_message(db: Session, message: dict):
    db_message = RawTelegramMessage(
        channel_name=message.get("channel_name"),
        message_id=message.get("id"),
        sender=message.get("sender"),
        timestamp=message.get("timestamp"),
        message=message.get("text"),
        media=message.get("media"),
        is_processed=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message