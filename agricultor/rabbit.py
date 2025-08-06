import pika
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Config desde .env
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

# Colas de envío (producir eventos)
COLAS_ENVIO = [
    os.getenv("RABBITMQ_PUBLISH_QUEUE", "eventos_cosecha"),
    os.getenv("RABBITMQ_PUBLISH_QUEUE_FACTURAS", "eventos_cosecha_facturas")
]

# Colas de recepción (escuchar respuestas)
COLAS_RESPUESTA = [
    os.getenv("RABBITMQ_CONSUME_QUEUE_INVENTARIO", "inventario_ajustado"),
    os.getenv("RABBITMQ_CONSUME_QUEUE_FACTURAS", "facturas_estado")
]

# Registro local de mensajes recibidos (opcional)
mensajes_recibidos = {cola: [] for cola in COLAS_RESPUESTA}


def get_connection():
    """Devuelve una conexión activa a RabbitMQ"""
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
    """Envía un evento JSON a todas las colas de salida"""
    connection = get_connection()
    channel = connection.channel()

    for cola in COLAS_ENVIO:
        if not cola:
            continue
        channel.queue_declare(queue=cola, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=cola,
            body=json.dumps(evento, ensure_ascii=False, default=str).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2  # persistente
            )
        )
        print(f"[➡️ Enviado] a '{cola}':\n{json.dumps(evento, indent=2, ensure_ascii=False)}")

    connection.close()


def callback(queue_name):
    def inner(ch, method, props, body):
        try:
            data = json.loads(body.decode("utf-8"))
            mensajes_recibidos[queue_name].append(data)
            print(f"\n📥 [Mensaje recibido en '{queue_name}']:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[❌ Error en '{queue_name}']: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    return inner


def iniciar_consumidores():
    """Escucha respuestas desde colas definidas"""
    connection = get_connection()
    channel = connection.channel()

    for cola in COLAS_RESPUESTA:
        if not cola:
            continue
        channel.queue_declare(queue=cola, durable=True)
        channel.basic_consume(queue=cola, on_message_callback=callback(cola))

    print(f"[*] Escuchando colas: {', '.join(COLAS_RESPUESTA)}")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("⛔ Interrumpido. Cerrando consumidor...")
        channel.stop_consuming()
    finally:
        connection.close()
