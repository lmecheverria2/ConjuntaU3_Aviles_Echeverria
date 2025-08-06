from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.cosecha import CosechaCreate, CosechaResponse
from app.models.cosecha import Cosecha
from database import get_db
from rabbit import enviar_evento

router = APIRouter(prefix="/cosechas", tags=["Cosechas"])

@router.post("/", response_model=CosechaResponse)
def crear_cosecha(cosecha: CosechaCreate, db: Session = Depends(get_db)):
    db_cosecha = Cosecha(
        id=str(cosecha.id),
        agricultor_id=cosecha.agricultor_id,
        producto=cosecha.producto,
        toneladas=cosecha.toneladas,
        estado="REGISTRADA",
        requiere_insumos=cosecha.requiere_insumos  # ✅ Se guarda en la BD
    )
    db.add(db_cosecha)
    db.commit()
    db.refresh(db_cosecha)

    # Enviar evento a RabbitMQ
    evento = {
        "event_id": str(cosecha.id),
        "event_type": "nueva_cosecha",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": {
            "cosecha_id": str(cosecha.id),
            "producto": cosecha.producto,
            "toneladas": cosecha.toneladas,
            "requiere_insumos": cosecha.requiere_insumos
        }
    }

    enviar_evento(evento)
    return db_cosecha

@router.get("/", response_model=list[CosechaResponse])
def listar_cosechas(db: Session = Depends(get_db)):
    return db.query(Cosecha).all()
