import os
import json
import uuid
import traceback
from dotenv import load_dotenv
import pika

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import SessionLocal
from app.models.factura import Factura

from app.models.precio import Precio

load_dotenv()

# ===== Precios referencia (USD/tonelada) =====

# ===== RabbitMQ =====
RABBITMQ_URL = os.getenv("RABBITMQ_URL")  # amqp://user:pass@host:5672/vhost  (opcional)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

QUEUE_CONSUME = os.getenv("RABBITMQ_CONSUME_QUEUE_FACTURAS", "eventos_cosecha_facturas")
QUEUE_PUBLISH = os.getenv("RABBITMQ_PUBLISH_QUEUE_FACTURAS", "facturas_estado")
PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH", "10"))

def _get_conn_channel():
    if RABBITMQ_URL:
        params = pika.URLParameters(RABBITMQ_URL)
    else:
        params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
            heartbeat=30,
            blocked_connection_timeout=300,
        )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_CONSUME, durable=True)
    channel.queue_declare(queue=QUEUE_PUBLISH, durable=True)
    channel.basic_qos(prefetch_count=PREFETCH_COUNT)
    return connection, channel

def _calcular_monto(db: Session, producto: str, toneladas: float) -> float:
    precio = db.query(Precio).filter(Precio.nombre == producto).first()
    if not precio:
        raise ValueError(f"Producto sin precio configurado en BD: '{producto}'")
    return round(float(toneladas) * float(precio.precio), 2)

def _crear_factura(db: Session, cosecha_id: str, monto: float) -> str:
    factura_id = str(uuid.uuid4())
    factura = Factura(
        id=factura_id,
        cosecha_id=cosecha_id,
        monto_total=monto,
        pagado=False,
    )
    db.add(factura)
    db.commit()
    return factura_id

def _publicar_estado(channel, factura_id: str):
    out_msg = {"estado": "FACTURADA", "factura_id": factura_id}
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_PUBLISH,
        body=json.dumps(out_msg, ensure_ascii=False).encode("utf-8"),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )

def _procesar(channel, method, properties, body: bytes):
    db = SessionLocal()
    try:
        data = json.loads(body.decode("utf-8"))
        if data.get("event_type") != "nueva_cosecha":
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        payload = data.get("payload", {})
        producto = payload.get("producto")
        toneladas = payload.get("toneladas")
        cosecha_id = payload.get("cosecha_id")
        if not (producto and toneladas and cosecha_id):
            raise ValueError("Mensaje incompleto: requiere 'producto', 'toneladas', 'cosecha_id'.")

        monto = _calcular_monto(db, producto, toneladas)
        factura_id = _crear_factura(db, cosecha_id, monto)
        _publicar_estado(channel, factura_id)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except IntegrityError as ie:
        # Probable duplicado por unique(cosecha_id)
        db.rollback()
        print("Factura ya existe para esa cosecha:", ie)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        db.rollback()
        print("Error procesando mensaje:", e)
        traceback.print_exc()
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        db.close()

def start_consumer():
    connection, channel = _get_conn_channel()
    print(f"[*] Facturas MS escuchando '{QUEUE_CONSUME}'. Publicará en '{QUEUE_PUBLISH}'. Ctrl+C para salir.")
    channel.basic_consume(queue=QUEUE_CONSUME, on_message_callback=_procesar)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nCerrando consumidor de facturas…")
    finally:
        if channel.is_open:
            channel.close()
        if connection.is_open:
            connection.close()
