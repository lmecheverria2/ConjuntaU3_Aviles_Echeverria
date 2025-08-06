# app/models/insumo.py
import enum
from sqlalchemy import String, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class TipoInsumoEnum(str, enum.Enum):
    semilla = "semilla"
    fertilizante = "fertilizante"

class Insumo(Base):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    stock: Mapped[float] = mapped_column(Float, nullable=False)
    tipo: Mapped[TipoInsumoEnum] = mapped_column(SAEnum(TipoInsumoEnum), nullable=False)
