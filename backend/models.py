from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    patient_type: Optional[str] = None
    appointment_data: Optional[Dict[str, Any]] = None