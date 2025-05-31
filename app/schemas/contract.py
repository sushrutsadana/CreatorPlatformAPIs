from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreatorBase(BaseModel):
    creator_name: str
    creator_email: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ContractResponse(BaseModel):
    status: str
    contract_text: str
    creator_id: str 