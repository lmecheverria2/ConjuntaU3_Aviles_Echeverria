from fastapi import FastAPI
from database import Base, engine
from app.models import insumo as insumo_model   # importa el modelo para registrar el mapeo
from app.routes import insumo as insumo_router

# Crear tablas (ya con el modelo importado)
Base.metadata.create_all(bind=engine)

# Inicializar la app FastAPI (sin elipsis)
app = FastAPI(
    title="API de Inventario",
    description="Gestión de insumos y actualización automática vía RabbitMQ",
    version="1.0.0",
)

# Rutas
app.include_router(insumo_router.router)

@app.get("/")
def root():
    return {"mensaje": "API de Inventario en funcionamiento"}
