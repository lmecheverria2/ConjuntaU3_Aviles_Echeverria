from fastapi import FastAPI
from database import Base, engine
from app.models import factura as factura_model
from rabbit import start_consumer
import threading

# Crea tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MS Facturas")

@app.on_event("startup")
def startup_event():
    # Levanta el consumidor de RabbitMQ en segundo plano
    threading.Thread(target=start_consumer, daemon=True).start()

@app.get("/")
def root():
    return {"status": "MS Facturas corriendo"}

if __name__ == "__main__":
    import uvicorn
    # Ejecuta la app en el puerto 8001
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)
