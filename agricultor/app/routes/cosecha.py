from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app.database import get_db
from app.models import agricultor as agricultor_models, cosecha as cosecha_models
from app.schemas import cosecha as schemas
from app.rabbit import publicar_evento

router = APIRouter(prefix="/cosechas", tags=["Cosechas"])

@router.post("/", response_model=schemas.CosechaOut)
def registrar_cosecha(data: schemas.CosechaCreate, db: Session = Depends(get_db)):
    agricultor = db.query(agricultor_models.Agricultor).filter(
        agricultor_models.Agricultor.id == str(data.agricultor_id)
    ).first()
    if not agricultor:
        raise HTTPException(status_code=404, detail="Agricultor no existe")

    cosecha_id = str(uuid4())
    cosecha = cosecha_models.Cosecha(id=cosecha_id, **data.dict())
    db.add(cosecha)
    db.commit()
    db.refresh(cosecha)

    publicar_evento("eventos_cosecha", {
        "evento": "nueva_cosecha",
        "payload": {
            "agricultor_id": cosecha.agricultor_id,
            "producto": cosecha.producto,
            "toneladas": cosecha.toneladas
        }
    })

    return cosecha

@router.get("/", response_model=list[schemas.CosechaOut])
def listar_cosechas(db: Session = Depends(get_db)):
    return db.query(cosecha_models.Cosecha).all()
