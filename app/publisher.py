import json
import os
import time
import pika
from dotenv import load_dotenv
from app.rabbitmq import get_connection, get_channel
from app.logger import log

load_dotenv()

QUEUE_RESULTADOS = os.getenv("QUEUE_RESULTADOS", "cola.resultados")


def publish_result(message: dict):
    start = time.perf_counter()
    transaction_id = message.get("transactionId", "")
    session_id = message.get("sessionId", "")
    try:
        conn = get_connection()
        channel = get_channel(conn)
        payload = json.dumps(message)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_RESULTADOS,
            body=payload,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        conn.close()
        duration = int((time.perf_counter() - start) * 1000)
        log("INFO", "message_published", "publisher",
            f"Mensaje publicado en {QUEUE_RESULTADOS}",
            transaction_id=transaction_id, session_id=session_id,
            status="SUCCESS", duration_ms=duration)
    except Exception as e:
        duration = int((time.perf_counter() - start) * 1000)
        log("ERROR", "publish_error", "publisher",
            "Error publicando mensaje",
            transaction_id=transaction_id, session_id=session_id,
            status="FAILED", duration_ms=duration, exc=e)
        raise


if __name__ == "__main__":
    test_message = {"tipo": "FASE", "contenido": "Test content", "fase": 1}
    publish_result(test_message)
    print("Published successfully")
