import json
import os
from dotenv import load_dotenv
from app.rabbitmq import get_connection, get_channel
from app.publisher import publish_result
from app.groq_client import generate_message

load_dotenv()

QUEUE_RECIBIDOS = os.getenv("QUEUE_RECIBIDOS", "cola.recibidos")
TOTAL_FASES = 5

_contadores = {}


def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        tipo = message["tipo"]
        contenido = message["contenido"]
        session_id = message["sessionId"]
        transaction_id = message["transactionId"]

        _contadores[transaction_id] = _contadores.get(transaction_id, 0) + 1
        fase = _contadores[transaction_id]

        print(f">>> Mensaje recibido — fase: {fase}/{TOTAL_FASES}, tipo: {tipo}, sessionId: {session_id}")

        if fase < TOTAL_FASES:
            publish_result({"tipo": tipo, "contenido": contenido, "sessionId": session_id, "transactionId": transaction_id})
            print(f">>> Fase {fase} reenviada — sessionId: {session_id}")
        else:
            texto_bonito = generate_message({"tipo": tipo, "contenido": contenido})
            publish_result({"tipo": tipo, "contenido": texto_bonito, "sessionId": session_id, "transactionId": transaction_id})
            print(f">>> Fase 5 (mensaje bonito) publicada — sessionId: {session_id}")
            del _contadores[transaction_id]

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consuming():
    conn = get_connection()
    channel = get_channel(conn)
    channel.basic_qos(prefetch_count=1)
    print(f">>> Registrando consumer en cola: {repr(QUEUE_RECIBIDOS)}")
    channel.basic_consume(queue=QUEUE_RECIBIDOS, on_message_callback=process_message)
    print(f">>> Consumer registrado. Iniciando start_consuming...")
    channel.start_consuming()
