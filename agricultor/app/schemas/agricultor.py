from pydantic import BaseModel
from typing import Optional

class AgricultorBase(BaseModel):
    nombre: str
    finca: str

class AgricultorCreate(AgricultorBase):
    pass

class AgricultorUpdate(AgricultorBase):
    pass

class AgricultorOut(AgricultorBase):
    id: str

    class Config:
        orm_mode = True
