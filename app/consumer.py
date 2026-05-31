import json
import os
from dotenv import load_dotenv
from app.rabbitmq import get_connection, get_channel
from app.publisher import publish_result
from app.groq_client import generate_message

load_dotenv()

QUEUE_RECIBIDOS = os.getenv("QUEUE_RECIBIDOS", "cola.recibidos")


def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        tipo = message["tipo"]
        contenido = message["contenido"]
        session_id = message["sessionId"]

        print(f">>> Mensaje recibido — tipo: {tipo}, sessionId: {session_id}")

        if tipo in ("EXITO", "ERROR"):
            texto_bonito = generate_message({"tipo": tipo, "contenido": contenido})
            publish_result({"tipo": "MENSAJE_BONITO", "contenido": texto_bonito, "sessionId": session_id})
            print(f">>> Mensaje generado: {texto_bonito}")
            print(f">>> Resultado publicado en cola.resultados — sessionId: {session_id}")

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
