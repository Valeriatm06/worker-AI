import os
import time
from groq import Groq
from dotenv import load_dotenv
from app.logger import log

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

_client = Groq(api_key=GROQ_API_KEY)


def generate_message(fase: dict) -> str:
    tipo = fase["tipo"]
    contenido = fase["contenido"]

    if tipo == "EXITO":
        tone_instruction = "El tono debe ser celebratorio y cálido."
    else:
        tone_instruction = "El tono debe ser empático y sugerir intentar de nuevo."

    prompt = (
        f"Transforma el siguiente resultado técnico de un pago en un mensaje empático "
        f"y amigable para el usuario, en máximo 2 oraciones en español. {tone_instruction}\n\n"
        f"Resultado técnico: {contenido}"
    )

    log("INFO", "llm_request", "groq_client", f"Enviando prompt al modelo {GROQ_MODEL}, tipo: {tipo}")
    start = time.perf_counter()
    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        duration = int((time.perf_counter() - start) * 1000)
        log("INFO", "llm_response", "groq_client",
            "Respuesta recibida del LLM",
            status="SUCCESS", duration_ms=duration)
        return response.choices[0].message.content.strip()
    except Exception as e:
        duration = int((time.perf_counter() - start) * 1000)
        log("ERROR", "llm_error", "groq_client",
            "Error al llamar al LLM",
            status="FAILED", duration_ms=duration, exc=e)
        raise


if __name__ == "__main__":
    result_exito = generate_message({"tipo": "EXITO", "contenido": "Pago procesado correctamente. Transacción ID: 12345."})
    print("EXITO:", result_exito)

    result_error = generate_message({"tipo": "ERROR", "contenido": "Fondos insuficientes en la cuenta."})
    print("ERROR:", result_error)
