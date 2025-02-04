from sqlalchemy import Column, Integer, BigInteger, Text, DateTime
from database import Base

class TelegramMessage(Base):
    __tablename__ = "telegram_messages"

    id = Column(Integer, primary_key=True, index=True, nullable=False)  # Primary Key
    channel_title = Column(Text)  # Channel title
    message_id = Column(BigInteger)  # Message ID (large number)
    message = Column(Text)  # Message content
    message_date = Column(DateTime)  # Timestamp without time zone
    media_path = Column(Text)  # Path to media files
    emoji = Column(Text)  # Emojis in message
    youtube = Column(Text)  # YouTube links in message
    phone = Column(Text)  # Phone numbers in message
