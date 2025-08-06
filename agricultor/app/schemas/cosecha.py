from pydantic import BaseModel, Field, ConfigDict
from typing import List
from uuid import UUID

class CosechaBase(BaseModel):
    agricultor_id: str
    producto: str
    toneladas: float
    requiere_insumos: List[str] = []

class CosechaCreate(CosechaBase):
    id: UUID = Field(..., alias="cosecha_id")

class CosechaResponse(CosechaBase):
    id: UUID
    estado: str

    model_config = ConfigDict(from_attributes=True)
