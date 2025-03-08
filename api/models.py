from sqlalchemy import Column, Integer, BigInteger, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class RawTelegramMessage(Base):
    __tablename__ = "raw_message"
    __table_args__ = {'extend_existing': True}  # Allow redefinition of the table
      # Allow redefinition of the table
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    channel_name = Column(Text)
    message_id = Column(BigInteger, unique=True) #added unique constraint
    sender = Column(Text)
    timestamp = Column(DateTime)
    message = Column(Text)
    media = Column(Text)
    is_processed = Column(Boolean, default=False)

    telegram_message = relationship("TelegramMessage", back_populates="raw_message")

class TelegramMessage(Base):
    __tablename__ = "telegram_messages"
    __table_args__ = {'extend_existing': True}  # Allow redefinition of the table
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    channel_title = Column(Text)
    message_id = Column(BigInteger, ForeignKey("raw_message.message_id", ondelete="CASCADE"), unique=True) #added unique constraint
    message = Column(Text)
    message_date = Column(DateTime)
    media_path = Column(Text)
    emoji = Column(Text)
    youtube = Column(Text)
    phone = Column(Text)

    raw_message = relationship("RawTelegramMessage", back_populates="telegram_message")

