from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class ActivityType(str, Enum):
    EMAIL_SENT = "email_sent"
    EMAIL_RECEIVED = "email_received"
    CALL_MADE = "call_made"
    CALL_COMPLETED = "call_completed"
    CREATOR_CREATED = "creator_created"
    STATUS_CHANGED = "status_changed"
    CALL_ANALYZED = "call_analyzed"

class CreatorCreate(BaseModel):
    name: str
    handle: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class Activity(BaseModel):
    creator_id: str
    activity_type: ActivityType
    body: str
    activity_datetime: datetime = datetime.now()

class CallRequest(BaseModel):
    prompt: str
    language: str = "en"
    voice: str = "nat"
    max_duration: int = 12

class EmailRequest(BaseModel):
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    from_email: Optional[str] = None 