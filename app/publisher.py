import json
import os
import pika
from dotenv import load_dotenv
from app.rabbitmq import get_connection, get_channel

load_dotenv()

QUEUE_RESULTADOS = os.getenv("QUEUE_RESULTADOS", "cola.resultados")


def publish_result(message: dict):
    conn = get_connection()
    channel = get_channel(conn)
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_RESULTADOS,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    conn.close()


if __name__ == "__main__":
    test_message = {"tipo": "FASE", "contenido": "Test content", "fase": 1}
    publish_result(test_message)
    print("Published successfully")
