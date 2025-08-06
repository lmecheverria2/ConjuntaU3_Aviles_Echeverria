from sqlalchemy import Column, String, Float, ForeignKey, JSON
from database import Base

class Cosecha(Base):
    __tablename__ = "cosechas"

    id = Column(String(36), primary_key=True, index=True)
    agricultor_id = Column(String(36), ForeignKey("agricultores.id"), nullable=False)
    producto = Column(String(100), nullable=False)
    toneladas = Column(Float, nullable=False)
    estado = Column(String(20), default="REGISTRADA")
    requiere_insumos = Column(JSON, nullable=False, default=[])  # Nuevo campo
