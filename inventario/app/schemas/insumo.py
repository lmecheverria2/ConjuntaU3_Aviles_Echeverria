from pydantic import BaseModel, Field
from enum import Enum

# Enum para tipos de insumos
class TipoInsumo(str, Enum):
    semilla = "semilla"
    fertilizante = "fertilizante"

# Campos base
class InsumoBase(BaseModel):
    nombre: str = Field(..., example="Semilla Arroz L-23")
    stock: float = Field(..., example=100.5)
    tipo: TipoInsumo = Field(..., example="semilla")

# Para creación de insumos (igual que base por ahora)
class InsumoCreate(InsumoBase):
    pass

# Para actualización de insumos (todos los campos opcionales)
class InsumoUpdate(BaseModel):
    nombre: str | None = Field(None, example="Fertilizante N-PK")
    stock: float | None = Field(None, example=50.0)
    tipo: TipoInsumo | None = Field(None, example="fertilizante")

# Para devolver datos de insumo desde la API
class InsumoResponse(InsumoBase):
    id: int

    class Config:
        orm_mode = True
