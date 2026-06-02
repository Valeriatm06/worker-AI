import json
import os
import time
from dotenv import load_dotenv
from app.rabbitmq import get_connection, get_channel
from app.publisher import publish_result
from app.groq_client import generate_message
from app.logger import log

load_dotenv()

QUEUE_RECIBIDOS = os.getenv("QUEUE_RECIBIDOS", "cola.recibidos")
TOTAL_FASES = 5

_contadores = {}


def process_message(ch, method, properties, body):
    start = time.perf_counter()
    transaction_id = ""
    session_id = ""
    try:
        message = json.loads(body)
        tipo = message["tipo"]
        contenido = message["contenido"]
        session_id = message["sessionId"]
        transaction_id = message["transactionId"]

        _contadores[transaction_id] = _contadores.get(transaction_id, 0) + 1
        fase = _contadores[transaction_id]

        log("INFO", "message_received", "consumer",
            f"Mensaje recibido — fase: {fase}/{TOTAL_FASES}, tipo: {tipo}",
            transaction_id=transaction_id, session_id=session_id)

        if fase < TOTAL_FASES:
            publish_result({"tipo": tipo, "contenido": contenido, "sessionId": session_id, "transactionId": transaction_id})
            duration = int((time.perf_counter() - start) * 1000)
            log("INFO", "phase_forwarded", "consumer",
                f"Fase {fase} reenviada",
                transaction_id=transaction_id, session_id=session_id,
                status="SUCCESS", duration_ms=duration)
        else:
            texto_bonito = generate_message({"tipo": tipo, "contenido": contenido})
            publish_result({"tipo": tipo, "contenido": texto_bonito, "sessionId": session_id, "transactionId": transaction_id})
            duration = int((time.perf_counter() - start) * 1000)
            log("INFO", "phase_final_published", "consumer",
                "Fase 5 (mensaje bonito) publicada",
                transaction_id=transaction_id, session_id=session_id,
                status="SUCCESS", duration_ms=duration)
            del _contadores[transaction_id]

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        duration = int((time.perf_counter() - start) * 1000)
        log("ERROR", "message_processing_error", "consumer",
            "Error procesando mensaje",
            transaction_id=transaction_id, session_id=session_id,
            status="FAILED", duration_ms=duration, exc=e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consuming():
    conn = get_connection()
    channel = get_channel(conn)
    channel.basic_qos(prefetch_count=1)
    log("INFO", "consumer_registered", "consumer",
        f"Registrando consumer en cola: {repr(QUEUE_RECIBIDOS)}")
    channel.basic_consume(queue=QUEUE_RECIBIDOS, on_message_callback=process_message)
    log("INFO", "consumer_started", "consumer", "Consumer registrado. Iniciando start_consuming...")
    channel.start_consuming()
