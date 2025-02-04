from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for Adding a New Message
class MessageCreate(BaseModel):
    user_input: str  # Required field
    channel_title: Optional[str] = "user input"  # Defaults to "user input"

# Schema for updating a message
class MessageUpdate(BaseModel):
    text: str  # The new text for the message


# Schema for Returning a Message (Response Model)
class MessageResponse(BaseModel):
    id: int
    message_id: int
    channel_title: str
    message: str
    message_date: datetime
    media_path: Optional[str] = None
    emoji: Optional[str] = None
    youtube: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True  # Allows ORM compatibility

# Schema for Deleting a Message (Response)
class MessageDeleteResponse(BaseModel):
    message: str


# Schema for the update response
class MessageUpdateResponse(BaseModel):
    message: str