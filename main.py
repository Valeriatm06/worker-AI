from dotenv import load_dotenv
from app.consumer import start_consuming

load_dotenv()

try:
    print("Worker IA iniciado. Esperando mensajes en cola.recibidos...")
    start_consuming()
except KeyboardInterrupt:
    print("Worker detenido.")
