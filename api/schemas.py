from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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
        from_attributes = True

class RawMessageResponse(BaseModel):
    id: int
    channel_name: str
    message_id: int
    sender: str
    timestamp: datetime
    message: str
    media: Optional[str] = None
    is_processed: bool

    class Config:
        from_attributes = True

# Schema for Paginated Raw Message Response
class PaginatedRawMessageResponse(BaseModel):
    total: int
    messages: List[RawMessageResponse]

# Schema for Paginated Response
class PaginatedMessageResponse(BaseModel):
    total: int
    messages: List[MessageResponse]

# Schema for Adding a New Message
class MessageCreate(BaseModel):
    user_input: str
    channel_title: Optional[str] = "user input"