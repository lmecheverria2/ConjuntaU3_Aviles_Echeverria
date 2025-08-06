from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.precio import PrecioCreate, PrecioUpdate, PrecioResponse
from app.models.precio import Precio
from database import get_db
from typing import List

router = APIRouter(prefix="/precios", tags=["Precios"])

@router.post("/", response_model=PrecioResponse)
def crear_precio(precio: PrecioCreate, db: Session = Depends(get_db)):
    nuevo = Precio(**precio.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=List[PrecioResponse])
def listar_precios(db: Session = Depends(get_db)):
    return db.query(Precio).all()

@router.put("/{precio_id}", response_model=PrecioResponse)
def actualizar_precio(precio_id: str, data: PrecioUpdate, db: Session = Depends(get_db)):
    p = db.query(Precio).filter(Precio.id == precio_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    for key, value in data.dict().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p

@router.delete("/{precio_id}")
def eliminar_precio(precio_id: str, db: Session = Depends(get_db)):
    p = db.query(Precio).filter(Precio.id == precio_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    db.delete(p)
    db.commit()
    return {"detalle": "Eliminado"}
