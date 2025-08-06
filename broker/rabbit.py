import pika
import os
import json
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

COLAS_ENVIO = ["eventos_cosecha", "eventos_cosecha_facturas"]
COLAS_RESPUESTA = ["inventario_ajustado", "facturas_estado"]

mensajes_recibidos = {
    "inventario_ajustado": [],
    "facturas_estado": [],
}

def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=30
    )
    return pika.BlockingConnection(params)

def enviar_evento(evento: dict):
    connection = get_connection()
    channel = connection.channel()
    for cola in COLAS_ENVIO:
        channel.queue_declare(queue=cola, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=cola,
            body=json.dumps(evento, ensure_ascii=False, default=str).encode("utf-8"),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
        print(f"[➡️ Enviado] a {cola}")
    connection.close()


def callback(queue_name):
    def inner(ch, method, props, body):
        try:
            data = json.loads(body.decode("utf-8"))
            mensajes_recibidos[queue_name].append(data)
            print(f"[📥 {queue_name}] Mensaje recibido:\n{json.dumps(data, indent=2, ensure_ascii=False)}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[❌ Error] en {queue_name} -> {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    return inner

def iniciar_consumidores():
    connection = get_connection()
    channel = connection.channel()
    for cola in COLAS_RESPUESTA:
        channel.queue_declare(queue=cola, durable=True)
        channel.basic_consume(queue=cola, on_message_callback=callback(cola))
    print(f"[*] Escuchando respuestas en {', '.join(COLAS_RESPUESTA)}")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Cerrando consumidor...")
        channel.stop_consuming()
    finally:
        connection.close()
