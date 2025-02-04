from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import crud
import schemas

app = FastAPI()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to add a new message
@app.post("/messages/", response_model=schemas.MessageResponse)
def add_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.add_telegram_message(db, message.user_input, message.channel_title)

# Endpoint to retrieve messages with a limit
@app.get("/messages/", response_model=list[schemas.MessageResponse])
def read_messages(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_telegram_messages(db, limit)

# Endpoint to retrieve messages based on channel_title and limit
@app.get("/messages/{channel_title}/", response_model=list[schemas.MessageResponse])
def read_messages_by_channel(channel_title: str, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_telegram_messages_by_channel(db, channel_title, limit)

# Endpoint to delete a message# Endpoint to delete a message by message_id
@app.delete("/messages/{message_id}/", response_model=schemas.MessageDeleteResponse)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    result = crud.delete_telegram_message(db, message_id)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return result

# Endpoint to update a message by message_id
@app.put("/messages/{message_id}/", response_model=schemas.MessageUpdateResponse)
def update_message(message_id: int, message_data: schemas.MessageUpdate, db: Session = Depends(get_db)):
    result = crud.update_telegram_message(db, message_id, message_data.text)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result
