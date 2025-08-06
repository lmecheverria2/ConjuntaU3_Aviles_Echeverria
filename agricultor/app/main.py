from fastapi import FastAPI
from app.routes import agricultor, cosecha
from app.database import Base, engine
from app.rabbit import setup_colas

setup_colas()


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservicio Central - Agricultores y Cosechas")
app.include_router(agricultor.router)
app.include_router(cosecha.router)
