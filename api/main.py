import json
import logging
import os,sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import Base, SessionLocal,engine
import crud
import schemas

sys.path.append(os.path.abspath(os.path.join('..', '')))

from app import mains, authenticate_telegram, check_auth_status

# Create tables on startup
app = FastAPI()

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication models
class TelegramAuthRequest(BaseModel):
    phone: str
    password: Optional[str] = None
    code: Optional[str] = None

class AuthStatusResponse(BaseModel):
    authenticated: bool
    error: Optional[str] = None

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication endpoints
@app.post("/auth/telegram", response_model=schemas.GenericResponse)
async def auth_telegram(auth_request: TelegramAuthRequest):
    """
    Authenticate with Telegram
    """
    try:
        result = await authenticate_telegram(
            auth_request.phone, 
            auth_request.password, 
            auth_request.code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/status", response_model=AuthStatusResponse)
async def get_auth_status():
    """
    Check Telegram authentication status
    """
    return await check_auth_status()

# Existing endpoints
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
    try:
        if all:
            messages = crud.get_all_messages(db)
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

@app.get("/messages/raw", response_model=schemas.PaginatedRawMessageResponse)
def read_raw_messages(
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Number of items per page", ge=1, le=100),
    channel_name: Optional[str] = Query(None, description="Filter by channel title"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (format: YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (format: YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
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
async def fetch_recent_messages(request: schemas.ChannelRequest, db: Session = Depends(get_db)):
    """
    Fetch recent messages and store them in the raw_message table.
    Requires Telegram authentication.
    """
    # Check authentication first
    auth_status = await check_auth_status()
    if not auth_status.get("authenticated"):
        raise HTTPException(
            status_code=401, 
            detail="Telegram authentication required. Please authenticate first."
        )

    result = await mains(request.channels)
    if result["status"] == "success" and "data" in result:
        try:
            messages, total = crud.insert_raw_messages(db, result["data"])
            return {"total": total, "messages": messages}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    elif result["status"] == "authentication_required":
        raise HTTPException(status_code=401, detail=result["message"])
    else:
        raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))

@app.post("/messages/process")
def process_messages_endpoint(db: Session = Depends(get_db)):
    try:
        result = crud.fetch_and_process_messages(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)