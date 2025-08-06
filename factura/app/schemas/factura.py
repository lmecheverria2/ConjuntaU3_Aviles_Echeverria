from datetime import datetime
from pydantic import BaseModel, ConfigDict

class FacturaBase(BaseModel):
    cosecha_id: str
    monto_total: float
    pagado: bool = False

class FacturaCreate(FacturaBase):
    pass

class FacturaResponse(FacturaBase):
    id: str
    creado_en: datetime
    model_config = ConfigDict(from_attributes=True)  # reemplaza orm_mode en v2
