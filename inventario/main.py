from fastapi import FastAPI
from database import Base, engine
from app.models import insumo as insumo_model
from app.routes import insumo as insumo_router
from rabbit import start_consumer
import threading

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Inventario",
    description="Gestión de insumos y actualización automática vía RabbitMQ",
    version="1.0.0",
)

app.include_router(insumo_router.router)

@app.get("/")
def root():
    return {"mensaje": "API de Inventario en funcionamiento"}

@app.on_event("startup")
def startup_event():
    # Ejecuta el consumidor de RabbitMQ en segundo plano
    threading.Thread(target=start_consumer, daemon=True).start()
