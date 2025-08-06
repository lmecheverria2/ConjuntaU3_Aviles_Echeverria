from sqlalchemy import Column, String
from database import Base

class Agricultor(Base):
    __tablename__ = "agricultores"
    id = Column(String(36), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    finca = Column(String(100), nullable=False)
