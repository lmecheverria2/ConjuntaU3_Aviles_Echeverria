from fastapi import FastAPI
from app.routes import agricultor, cosecha
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservicio Central - Agricultores y Cosechas")
app.include_router(agricultor.router)
app.include_router(cosecha.router)
