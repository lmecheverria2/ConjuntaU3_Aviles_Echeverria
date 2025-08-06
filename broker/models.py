from pydantic import BaseModel
from typing import List
from datetime import datetime

class Payload(BaseModel):
    cosecha_id: str
    producto: str
    toneladas: float
    requiere_insumos: List[str]

class EventoCosecha(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    payload: Payload
