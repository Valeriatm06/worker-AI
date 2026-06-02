from dotenv import load_dotenv
from app.consumer import start_consuming
from app.logger import log

load_dotenv()

try:
    log("INFO", "worker_started", "worker", "Worker IA iniciado. Esperando mensajes en cola.recibidos...")
    start_consuming()
except KeyboardInterrupt:
    log("INFO", "worker_stopped", "worker", "Worker detenido.")
