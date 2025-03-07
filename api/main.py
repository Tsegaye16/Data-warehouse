import json
import logging
import os,sys
from fastapi import FastAPI, Depends, HTTPException, Query

from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal
import crud
import schemas

sys.path.append(os.path.abspath(os.path.join('..', 'scripts')))

from telegram_scrapper import TelegramScraper

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to retrieve messages with pagination
@app.get("/messages/", response_model=schemas.PaginatedMessageResponse)
def read_messages(
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieve messages with pagination.
    :param page: Page number (starting from 1)
    :param page_size: Number of items per page
    :param db: Database session
    :return: Paginated response with messages and total count
    """
    try:
        # Calculate skip value for pagination
        skip = (page - 1) * page_size
        # Fetch messages and total count from the database
        messages, total = crud.get_telegram_messages(db, skip=skip, limit=page_size)
        # Return paginated response
        return {"total": total, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Endpoint to retrieve raw messages with pagination

# Endpoint to retrieve raw messages with pagination
@app.get("/messages/raw", response_model=schemas.PaginatedRawMessageResponse) #Modified line
def read_raw_messages(
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of items per page", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieve raw messages with pagination.
    :param page: Page number (starting from 1)
    :param page_size: Number of items per page
    :param db: Database session
    :return: Paginated response with raw messages and total count
    """
    try:
        skip = (page - 1) * page_size
        messages, total = crud.get_raw_telegram_message(db, skip=skip, limit=page_size)
        return {"total": total, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Endpoint to add a new message
@app.post("/messages/", response_model=schemas.MessageResponse)
def add_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.add_telegram_message(db, message.user_input, message.channel_title)



# Endpoint to retrieve messages based on channel_title and limit
@app.get("/messages/{channel_title}/", response_model=list[schemas.MessageResponse])
def read_messages_by_channel(channel_title: str, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_telegram_messages_by_channel(db, channel_title, limit)


# Make the endpoint asynchronous
@app.post("/messages/recent")
async def fetch_recent_messages(db: Session = Depends(get_db)):
    scraper =await TelegramScraper()
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

    metadata = {}
    if os.path.exists(metadata_fetch_file):
        with open(metadata_fetch_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    all_messages = []
    for channel in channels:
        last_fetched_id = metadata.get(channel, {}).get("last_fetched_id")
        try:
            # Use await to call asynchronous fetch_messages
            messages = await scraper.fetch_messages(channel, limit=200, min_id=last_fetched_id)
            if messages:
                all_messages.extend(messages)
                metadata[channel] = {
                    "last_fetched_id": messages[0]["id"],
                    "last_fetched_time": messages[0]["timestamp"]
                }
        except Exception as e:
            logging.error(f"Error fetching from {channel}: {e}")

    with open(metadata_fetch_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    for message in all_messages:
        crud.add_raw_telegram_message(db, message)

    return {"message": "Recent messages fetched and saved."}

