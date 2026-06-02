imp# Worker IA — EnVivo

Worker en Python que consume mensajes de resultados de pago desde RabbitMQ, genera un mensaje empático usando la API de Groq (LLM) y publica el resultado en otra cola para ser entregado al frontend.

## Flujo

```
cola.recibidos  →  Worker IA (Groq)  →  cola.resultados
```

1. La aplicación Java publica el resultado del pago en `cola.recibidos`.
2. El worker consume el mensaje, lo procesa con un modelo de lenguaje y genera un mensaje amigable para el usuario.
3. El resultado se publica en `cola.resultados` junto con el `sessionId` para identificar al usuario.

## Requisitos

- Python 3.10+
- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado y corriendo
- API key de [Groq](https://console.groq.com)

## Levantar RabbitMQ

El proyecto incluye un `docker-compose.yml` con RabbitMQ preconfigurado. Levántalo antes de ejecutar el worker:

```bash
docker compose up -d
```

Esto inicia RabbitMQ con:
- **Usuario:** `admin` / **Contraseña:** `admin123`
- **Puerto AMQP:** `5672`
- **Panel de administración:** [http://localhost:15672](http://localhost:15672)

Para detenerlo:

```bash
docker compose down
```

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Copia el archivo de ejemplo y completa los valores:

```bash
cp .env.example .env
```

| Variable           | Descripción                                | Valor por defecto      |
|--------------------|--------------------------------------------|------------------------|
| `RABBITMQ_HOST`    | Host de RabbitMQ                           | `localhost`            |
| `RABBITMQ_PORT`    | Puerto de RabbitMQ                         | `5672`                 |
| `RABBITMQ_USER`    | Usuario de RabbitMQ                        | `admin`                |
| `RABBITMQ_PASS`    | Contraseña de RabbitMQ                     | `admin123`             |
| `QUEUE_RECIBIDOS`  | Cola de entrada (mensajes del gateway)     | `cola.recibidos`       |
| `QUEUE_RESULTADOS` | Cola de salida (mensajes generados por IA) | `cola.resultados`      |
| `GROQ_API_KEY`     | API key de Groq                            | —                      |
| `GROQ_MODEL`       | Modelo de Groq a usar                      | `llama-3.1-8b-instant` |

## Ejecución

```bash
python main.py
```

Salida esperada:

```
Worker IA iniciado. Esperando mensajes en cola.recibidos...
>>> Registrando consumer en cola: 'cola.recibidos'
>>> Consumer registrado. Iniciando start_consuming...
>>> Mensaje recibido — tipo: EXITO, sessionId: <id>
>>> Mensaje generado: ¡Tu pago fue aprobado exitosamente! ...
>>> Resultado publicado en cola.resultados — sessionId: <id>
```

## Estructura

```
worker-ai/
├── app/
│   ├── consumer.py      # Consume cola.recibidos y orquesta el procesamiento
│   ├── publisher.py     # Publica resultados en cola.resultados
│   ├── groq_client.py   # Llama a la API de Groq para generar el mensaje
│   └── rabbitmq.py      # Conexión y declaración de colas
├── main.py              # Punto de entrada
├── requirements.txt
├── .env.example
└── README.md
```

## Formato de mensajes

**Entrada (`cola.recibidos`):**
```json
{
  "tipo": "EXITO" | "ERROR",
  "contenido": "Mensaje técnico del gateway de pago",
  "sessionId": "identificador de sesión del usuario"
}
```

**Salida (`cola.resultados`):**
```json
{
  "tipo": "MENSAJE_BONITO",
  "contenido": "Mensaje empático generado por IA",
  "sessionId": "identificador de sesión del usuario"
}
```
