from pydantic import BaseModel, UUID4, Field
from typing import Optional

class CosechaBase(BaseModel):
    agricultor_id: UUID4
    producto: str
    toneladas: float

class CosechaCreate(CosechaBase):
    pass

class CosechaOut(CosechaBase):
    id: UUID4
    estado: str

    class Config:
        orm_mode = True
