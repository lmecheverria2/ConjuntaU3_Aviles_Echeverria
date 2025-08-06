import json
import os
import sys
import traceback
import pika
from dotenv import load_dotenv

from sqlalchemy.orm import Session
from database import SessionLocal  # de tu database.py
from app.models.insumo import Insumo, TipoInsumoEnum  # tu modelo ORM

# === Carga de variables de entorno ===
load_dotenv()

# Puedes usar una URL completa o los campos separados.
RABBITMQ_URL = os.getenv("RABBITMQ_URL")  # amqp://user:pass@host:5672/vhost
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

QUEUE_CONSUME = os.getenv("RABBITMQ_CONSUME_QUEUE", "eventos_cosecha")
QUEUE_PUBLISH = os.getenv("RABBITMQ_PUBLISH_QUEUE", "inventario_ajustado")
print("Conectando a RabbitMQ:", {
    "url": bool(RABBITMQ_URL),
    "host": RABBITMQ_HOST,
    "port": RABBITMQ_PORT,
    "user": RABBITMQ_USER,
    "vhost": RABBITMQ_VHOST,
    "consume": QUEUE_CONSUME,
    "publish": QUEUE_PUBLISH,
})

# === Parámetros de consumo ===
PREFETCH_COUNT = int(os.getenv("RABBITMQ_PREFETCH", "10"))

# === Reglas de consumo por tonelada ===
KG_SEMILLA_POR_TON = 5.0
KG_FERTILIZANTE_POR_TON = 2.0


def get_connection_and_channel():
    """Crea conexión y canal con RabbitMQ."""
    if RABBITMQ_URL:
        params = pika.URLParameters(RABBITMQ_URL)
    else:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
            credentials=credentials,
            heartbeat=30,
            blocked_connection_timeout=300,
        )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    # Declaración idempotente de colas (durables)
    channel.queue_declare(queue=QUEUE_CONSUME, durable=True)
    channel.queue_declare(queue=QUEUE_PUBLISH, durable=True)
    # Evita inundar al consumidor
    channel.basic_qos(prefetch_count=PREFETCH_COUNT)
    return connection, channel


def ajustar_stock(db: Session, nombre_insumo: str, cantidad_kg: float) -> dict:
    """
    Descuenta 'cantidad_kg' del stock del insumo indicado.
    Devuelve datos para telemetría/publicación.
    """
    ins = db.query(Insumo).filter(Insumo.nombre == nombre_insumo).first()
    if not ins:
        raise ValueError(f"Insumo '{nombre_insumo}' no encontrado")

    stock_anterior = float(ins.stock)
    ins.stock = stock_anterior - float(cantidad_kg)
    db.add(ins)
    db.commit()
    db.refresh(ins)

    return {
        "nombre": ins.nombre,
        "tipo": ins.tipo.value if hasattr(ins.tipo, "value") else str(ins.tipo),
        "descuento_kg": cantidad_kg,
        "stock_anterior": stock_anterior,
        "stock_actual": float(ins.stock),
    }


def calcular_descuentos(db: Session, requiere_insumos: list[str], toneladas: float) -> list[dict]:
    """
    Para los nombres de 'requiere_insumos', determina si son semilla o fertilizante
    (leyendo el tipo desde BD) y calcula el descuento correspondiente.
    """
    resultados = []
    for nombre in requiere_insumos:
        ins = db.query(Insumo).filter(Insumo.nombre == nombre).first()
        if not ins:
            raise ValueError(f"Insumo requerido no existe en BD: '{nombre}'")

        if ins.tipo == TipoInsumoEnum.semilla:
            cantidad = toneladas * KG_SEMILLA_POR_TON
        elif ins.tipo == TipoInsumoEnum.fertilizante:
            cantidad = toneladas * KG_FERTILIZANTE_POR_TON
        else:
            raise ValueError(f"Tipo de insumo desconocido para '{nombre}': {ins.tipo}")

        resultados.append({"nombre": nombre, "cantidad_kg": cantidad})
    return resultados


def publicar_ajuste(channel, payload: dict):
    """Publica mensaje de confirmación en la cola de inventario ajustado."""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_PUBLISH,
        body=body,
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,  # persistente
        ),
    )


def procesar_mensaje(channel, method, properties, body: bytes):
    """Callback principal de consumo."""
    db = SessionLocal()
    try:
        data = json.loads(body.decode("utf-8"))
        event_id = data.get("event_id")
        event_type = data.get("event_type")
        payload = data.get("payload", {})
        toneladas = float(payload.get("toneladas", 0))
        requiere_insumos = payload.get("requiere_insumos", [])

        if event_type != "nueva_cosecha":
            raise ValueError(f"Tipo de evento no soportado: {event_type}")

        # 1) Determinar descuentos por tipo a partir de BD
        descuentos = calcular_descuentos(db, requiere_insumos, toneladas)

        # 2) Aplicar descuentos
        ajustes_aplicados = []
        for d in descuentos:
            ajustes_aplicados.append(ajustar_stock(db, d["nombre"], d["cantidad_kg"]))

        # 3) Publicar confirmación
        out_msg = {
            "event_id": event_id,
            "evento_origen": event_type,
            "resultado": "ok",
            "detalle_ajustes": ajustes_aplicados,
        }
        publicar_ajuste(channel, out_msg)

        # ACK
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # Log de error
        print("Error procesando mensaje:", e, file=sys.stderr)
        traceback.print_exc()
        # NACK sin reenqueue para evitar loop si el mensaje es inválido
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        db.close()


def main():
    connection, channel = get_connection_and_channel()
    print(f"[*] Esperando mensajes en '{QUEUE_CONSUME}'. Ctrl+C para salir.")
    channel.basic_consume(queue=QUEUE_CONSUME, on_message_callback=procesar_mensaje)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nCerrando consumidor…")
    finally:
        if channel.is_open:
            channel.close()
        if connection.is_open:
            connection.close()


def start_consumer():
    connection, channel = get_connection_and_channel()
    print(f"[*] Inventario escuchando '{QUEUE_CONSUME}'. Ctrl+C para salir.")
    channel.basic_consume(queue=QUEUE_CONSUME, on_message_callback=procesar_mensaje)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nCerrando consumidor…")
    finally:
        if channel.is_open:
            channel.close()
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
