import json
import logging
import os,sys
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import Base, SessionLocal,engine
import crud
import schemas

sys.path.append(os.path.abspath(os.path.join('..', '')))


from app import mains
# Create tables on startup

app = FastAPI()
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)



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
    all: bool = Query(False, description="Return all messages if True"),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of items per page", ge=1),
    channel_name: Optional[str] = Query(None, description="Filter by channel title"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (format: YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (format: YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Retrieve messages with optional pagination and filters.
    If `all=True`, returns all messages.
    Otherwise, applies pagination and optional filters (channel_name, start_date, end_date).
    """
    try:
        if all:
            messages = crud.get_all_messages(db)  # Fetch all messages
            total = len(messages)
        else:
            skip = (page - 1) * page_size
            messages, total = crud.get_telegram_messages(
                db,
                skip=skip,
                limit=page_size,
                channel_title=channel_name,
                start_date=start_date,
                end_date=end_date,
            )

        return {"total": total, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to retrieve raw messages with pagination and optional channel_title filter
@app.get("/messages/raw", response_model=schemas.PaginatedRawMessageResponse)
def read_raw_messages(
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of items per page", ge=1, le=100),
    channel_name: Optional[str] = Query(None, description="Filter by channel title"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (format: YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (format: YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve raw messages with pagination and optional filters.
    :param page: Page number (starting from 1)
    :param page_size: Number of items per page
    :param channel_name: Optional filter by channel title
    :param start_date: Optional filter by start date
    :param end_date: Optional filter by end date
    :param db: Database session
    :return: Paginated response with raw messages and total count
    """
    try:
        skip = (page - 1) * page_size
        messages, total = crud.get_raw_telegram_message(
            db,
            skip=skip,
            limit=page_size,
            channel_name=channel_name,
            start_date=start_date,
            end_date=end_date,
        )
        return {"total": total, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/messages/recent")
async def fetch_recent_messages(db: Session = Depends(get_db)):
    """
    Fetch recent messages and store them in the raw_message table.
    """
    result = await mains()  # Fetch messages
    if result["status"] == "success" and "data" in result:
        try:
            total,messages=  crud.insert_raw_messages(db, result["data"])  # Insert into database
            
            return {"total": total, "messages": messages}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    else:
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))


@app.post("/messages/process")
def process_messages_endpoint(db: Session = Depends(get_db)):
    """
    Process all unprocessed messages by cleaning and inserting them into the telegram_messages table.
    """
    try:
        result = crud.fetch_and_process_messages(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


