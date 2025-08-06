import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

def publicar_evento(nombre_cola: str, mensaje: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # ⚠️ DECLARAR LA COLA ANTES DE PUBLICAR
    channel.queue_declare(queue=nombre_cola, durable=True)

    # Enviar el mensaje
    body = json.dumps(mensaje, ensure_ascii=False).encode("utf-8")
    channel.basic_publish(
        exchange="",
        routing_key=nombre_cola,
        body=body,
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2  # Hacer el mensaje persistente
        )
    )
    connection.close()

def setup_colas():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    for cola in ["eventos_cosecha", "eventos_cosecha_facturas"]:
        channel.queue_declare(queue=cola, durable=True)
        print(f"Cola declarada: {cola}")

    connection.close()

