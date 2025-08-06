from fastapi import FastAPI
import threading
from models import EventoCosecha
from rabbit import enviar_evento, iniciar_consumidores, mensajes_recibidos

app = FastAPI(title="Broker de Eventos de Cosecha")

@app.on_event("startup")
def startup():
    threading.Thread(target=iniciar_consumidores, daemon=True).start()

@app.get("/")
def root():
    return {"message": "Broker en funcionamiento"}

@app.post("/enviar")
def enviar_evento_a_colas(evento: EventoCosecha):
    enviar_evento(evento.model_dump())
    return {"status": "enviado", "event_id": evento.event_id}

@app.get("/mensajes/inventario")
def ver_inventario_ajustado():
    return mensajes_recibidos["inventario_ajustado"]

@app.get("/mensajes/facturas")
def ver_facturas_estado():
    return mensajes_recibidos["facturas_estado"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
