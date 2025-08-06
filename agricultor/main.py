from fastapi import FastAPI
from database import Base, engine
from app.models import cosecha as cosecha_model
from app.models import agricultor as agricultor_model
from app.routes import cosecha as cosecha_router, agricultor as agricultor_router

import threading
from rabbit import iniciar_consumidores

# Crear tablas (en producción usar migraciones como Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MS Cosechas")

# Rutas
app.include_router(cosecha_router.router)
app.include_router(agricultor_router.router)

# Consumidores RabbitMQ en background
@app.on_event("startup")
def startup_event():
    threading.Thread(target=iniciar_consumidores, daemon=True).start()

@app.get("/")
def root():
    return {"status": "MS Cosechas activo"}
