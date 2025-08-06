import os
import json
import pika
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.cosecha import Cosecha

load_dotenv()

# Configuración RabbitMQ desde .env o default
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

# Colas de envío y respuesta (puedes usar env vars si quieres)
COLAS_ENVIO = ["eventos_cosecha", "eventos_cosecha_facturas"]
COLAS_RESPUESTA = ["inventario_ajustado", "facturas_estado"]

def conectar():
    creds = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=creds,
        heartbeat=30,
        blocked_connection_timeout=300,
    )
    return pika.BlockingConnection(params)

def setup_queues():
    conexion = conectar()
    canal = conexion.channel()
    # Declarar colas durables
    for cola in COLAS_ENVIO + COLAS_RESPUESTA:
        canal.queue_declare(queue=cola, durable=True)
    conexion.close()

def publicar_evento(cola: str, mensaje: dict):
    conexion = conectar()
    canal = conexion.channel()
    canal.basic_publish(
        exchange="",
        routing_key=cola,
        body=json.dumps(mensaje),
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2  # mensaje persistente
        )
    )
    conexion.close()

def procesar_mensaje_inventario(channel, method, properties, body):
    # Ejemplo: Procesar mensaje de inventario ajustado
    try:
        data = json.loads(body.decode())
        print("[Inventario] Mensaje recibido:", data)
        # Aquí puedes insertar lógica con DB o lo que necesites
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Error procesando mensaje inventario:", e)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def procesar_mensaje_facturas(channel, method, properties, body):
    # Ejemplo: Procesar mensaje estado facturas
    try:
        data = json.loads(body.decode())
        print("[Facturas] Mensaje recibido:", data)
        # Aquí tu lógica para facturas
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("Error procesando mensaje facturas:", e)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def consumir_colas():
    conexion = conectar()
    canal = conexion.channel()

    # Consumir cola inventario_ajustado
    canal.basic_consume(queue="inventario_ajustado", on_message_callback=procesar_mensaje_inventario)
    # Consumir cola facturas_estado
    canal.basic_consume(queue="facturas_estado", on_message_callback=procesar_mensaje_facturas)

    print("Esperando mensajes en inventario_ajustado y facturas_estado. Ctrl+C para salir.")
    try:
        canal.start_consuming()
    except KeyboardInterrupt:
        print("Interrupción por teclado. Cerrando consumidor...")
    finally:
        if canal.is_open:
            canal.close()
        if conexion.is_open:
            conexion.close()

# Ejemplo simple para publicar un mensaje de cosecha
def publicar_cosecha(mensaje: dict):
    # Publica en la cola 'eventos_cosecha'
    publicar_evento("eventos_cosecha", mensaje)

if __name__ == "__main__":
    # Preparar colas
    setup_queues()

    # Ejemplo: publicar mensaje
    msg = {"id": 1, "toneladas": 10, "fecha": "2025-08-06"}
    publicar_cosecha(msg)

    # Iniciar consumo de respuestas
    consumir_colas()
