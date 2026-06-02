import csv
import io
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

_logger = logging.getLogger("csv")
_logger.propagate = False
_logger.setLevel(logging.DEBUG)

if not _logger.handlers:
    _fmt = logging.Formatter("%(message)s")
    _sh = logging.StreamHandler(sys.stdout)
    _sh.setFormatter(_fmt)
    _logger.addHandler(_sh)
    _fh = logging.FileHandler("logs/app.log", encoding="utf-8")
    _fh.setFormatter(_fmt)
    _logger.addHandler(_fh)

_LEVEL_MAP = {
    "INFO": logging.INFO,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "SUCCESS": logging.INFO,
    "FAILED": logging.ERROR,
}


def log(
    level: str,
    event: str,
    module: str,
    message: str,
    transaction_id: str = "",
    session_id: str = "",
    user_id: str = "",
    client_ip: str = "",
    payment_provider: str = "",
    status: str = "",
    error_code: str = "",
    duration_ms: str = "",
    exc: Exception = None,
):
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
    log_id = str(uuid.uuid4())

    if exc is not None:
        message = f"{message} | throwable={type(exc).__name__}: {exc}"

    row = [
        timestamp,
        log_id,
        level,
        event,
        module,
        transaction_id,
        session_id,
        user_id,
        client_ip,
        payment_provider,
        status,
        error_code,
        str(duration_ms) if duration_ms != "" else "",
        message,
    ]

    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(row)
    _logger.log(_LEVEL_MAP.get(level, logging.INFO), buf.getvalue().rstrip("\r\n"))
