from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)               # UUID en texto
    cosecha_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    monto_total: Mapped[float] = mapped_column(Float, nullable=False)
    pagado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
