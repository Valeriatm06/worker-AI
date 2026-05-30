import os
import pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
QUEUE_RECIBIDOS = os.getenv("QUEUE_RECIBIDOS", "cola.recibidos")
QUEUE_RESULTADOS = os.getenv("QUEUE_RESULTADOS", "cola.resultados")


def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
    )
    return pika.BlockingConnection(parameters)


def get_channel(connection):
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_RECIBIDOS, durable=True)
    channel.queue_declare(queue=QUEUE_RESULTADOS, durable=True)
    return channel


if __name__ == "__main__":
    try:
        conn = get_connection()
        get_channel(conn)
        conn.close()
        print("RabbitMQ connection successful")
    except Exception as e:
        print(f"Connection failed: {e}")
