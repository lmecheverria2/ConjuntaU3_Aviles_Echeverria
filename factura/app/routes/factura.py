from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from app.models.factura import Factura
from app.schemas.factura import FacturaResponse

router = APIRouter(
    prefix="/facturas",
    tags=["Facturas"]
)

@router.get("/", response_model=List[FacturaResponse])
def obtener_facturas(db: Session = Depends(get_db)):
    return db.query(Factura).all()
