from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from database import get_db
from app.models import agricultor as models
from app.schemas import agricultor as schemas

router = APIRouter(prefix="/agricultores", tags=["Agricultores"])

@router.post("/", response_model=schemas.AgricultorOut)
def crear_agricultor(data: schemas.AgricultorCreate, db: Session = Depends(get_db)):
    agricultor = models.Agricultor(id=str(uuid4()), **data.dict())
    db.add(agricultor)
    db.commit()
    db.refresh(agricultor)
    return agricultor

@router.get("/", response_model=list[schemas.AgricultorOut])
def listar_agricultores(db: Session = Depends(get_db)):
    return db.query(models.Agricultor).all()

@router.put("/{id}", response_model=schemas.AgricultorOut)
def actualizar_agricultor(id: str, data: schemas.AgricultorUpdate, db: Session = Depends(get_db)):
    agricultor = db.query(models.Agricultor).filter(models.Agricultor.id == id).first()
    if not agricultor:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")
    for k, v in data.dict().items():
        setattr(agricultor, k, v)
    db.commit()
    db.refresh(agricultor)
    return agricultor

@router.delete("/{id}")
def eliminar_agricultor(id: str, db: Session = Depends(get_db)):
    agricultor = db.query(models.Agricultor).filter(models.Agricultor.id == id).first()
    if not agricultor:
        raise HTTPException(status_code=404, detail="Agricultor no encontrado")
    db.delete(agricultor)
    db.commit()
    return {"ok": True}
