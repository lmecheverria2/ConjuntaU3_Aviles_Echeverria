from pydantic import BaseModel
from uuid import UUID

class PrecioBase(BaseModel):
    nombre: str
    precio: float

class PrecioCreate(PrecioBase):
    pass

class PrecioUpdate(PrecioBase):
    pass

class PrecioResponse(PrecioBase):
    id: str

    class Config:
        from_attributes = True
