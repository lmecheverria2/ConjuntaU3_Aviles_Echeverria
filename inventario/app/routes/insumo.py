from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from database import get_db
from app.schemas.insumo import InsumoCreate, InsumoUpdate, InsumoResponse
from app.models.insumo import Insumo

router = APIRouter(prefix="/insumos", tags=["Insumos"])

@router.post("/", response_model=InsumoResponse)
def crear_insumo(insumo: InsumoCreate, db: Session = Depends(get_db)):
    nuevo_insumo = Insumo(**insumo.model_dump())  # Pydantic v2
    db.add(nuevo_insumo)
    db.commit()
    db.refresh(nuevo_insumo)
    return nuevo_insumo

@router.get("/", response_model=List[InsumoResponse])
def listar_insumos(db: Session = Depends(get_db)):
    return db.execute(select(Insumo)).scalars().all()

@router.get("/{insumo_id}", response_model=InsumoResponse)
def obtener_insumo(insumo_id: int, db: Session = Depends(get_db)):
    insumo = db.get(Insumo, insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return insumo

@router.put("/{insumo_id}", response_model=InsumoResponse)
def actualizar_insumo(insumo_id: int, datos: InsumoUpdate, db: Session = Depends(get_db)):
    insumo = db.get(Insumo, insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    for key, value in datos.model_dump(exclude_unset=True).items():
        setattr(insumo, key, value)
    db.commit()
    db.refresh(insumo)
    return insumo

@router.delete("/{insumo_id}")
def eliminar_insumo(insumo_id: int, db: Session = Depends(get_db)):
    insumo = db.get(Insumo, insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    db.delete(insumo)
    db.commit()
    return {"mensaje": "Insumo eliminado correctamente"}
