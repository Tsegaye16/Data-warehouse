import random
from sqlalchemy.orm import Session
from models import TelegramMessage
import sys, os
import pandas as pd
from datetime import datetime
import schemas

sys.path.append(os.path.abspath(os.path.join('../scripts')))

from data_cleaning import DataFrameCleaner

def get_telegram_messages(db: Session, limit: int):
    return db.query(TelegramMessage).limit(limit).all()

# Function to retrieve messages by channel_title with a limit
def get_telegram_messages_by_channel(db: Session, channel_title: str, limit: int):
    return db.query(TelegramMessage).filter(TelegramMessage.channel_title == channel_title).limit(limit).all()

def delete_telegram_message(db: Session, message_id: int):
    # Fetch the message by message_id
    message = db.query(TelegramMessage).filter(TelegramMessage.message_id == message_id).first()
    
    if message:
        # Delete the message
        db.delete(message)
        db.commit()
        return {"message": f"Message with ID {message_id} deleted successfully."}
    else:
        return {"error": f"Message with ID {message_id} not found."}
    
def generate_message_id(db: Session) -> int:
    """
    Generate a random, unique message_id.
    """
    while True:
        message_id = random.randint(1000000000, 9999999999)  # Generate a 10-digit random number
        if not db.query(TelegramMessage).filter(TelegramMessage.message_id == message_id).first():
            return message_id

def add_telegram_message(db: Session, user_input: str, channel_title: str = "user input") -> schemas.MessageResponse:
    """
    Add a message to the database after cleaning the user input.
    """

    # Convert user input to DataFrame
    df = pd.DataFrame([{'text': user_input}])
    print(user_input)
    # Initialize DataFrameCleaner with the input data
    cleaner = DataFrameCleaner(df)

    # Perform cleaning steps
    df = cleaner.clean_text()  # Clean the text
    df = cleaner.extract_links()  # Extract YouTube links, websites, and phone numbers
    df = cleaner.remove_duplicates()  # Remove duplicates if any

    # Generate a unique message_id
    message_id = generate_message_id(db)

    # Create a new TelegramMessage object
    new_message = TelegramMessage(
        message_id=message_id,
        channel_title=channel_title,  # Default is "user input" if not provided
        message=df['text'].iloc[0],  # Get the cleaned text
        media_path="",  # Placeholder for media paths
        emoji=df.get('emoji', pd.Series([""])).iloc[0],  # Handle missing emoji column safely
        youtube=df.get('youtube', pd.Series([""])).iloc[0],  # Handle missing YouTube column safely
        phone=df.get('phone', pd.Series([""])).iloc[0],  # Handle missing phone number column safely
        message_date=datetime.utcnow()  # Use current timestamp
    )

    # Add the new message to the database
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message  # Pydantic will serialize it using the response model

def update_telegram_message(db: Session, message_id: int, new_text: str):
    # Fetch the message by message_id
    message = db.query(TelegramMessage).filter(TelegramMessage.message_id == message_id).first()
    print("Message: ", message.message)
    if not message:
        return {"error": f"Message with ID {message_id} not found."}

    # Update the message text
    message.message = new_text
    db.commit()
    db.refresh(message)  # Refresh to get updated data
    
    return {"message": f"Message with ID {message_id} updated successfully."}