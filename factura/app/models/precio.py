import uuid
from sqlalchemy import Column, String, Float
from database import Base

class Precio(Base):
    __tablename__ = "precios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, unique=True, nullable=False)
    precio = Column(Float, nullable=False)
