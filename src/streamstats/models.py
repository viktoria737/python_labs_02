from dataclasses import dataclass
from datetime import datetime

from .errors import InvalidEventError, InvalidTimestampError

VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

@dataclass
class Event:
    """Представление одного события лога."""
    timestamp: datetime
    level: str
    source: str
    message: str


def parse_timestamp(ts_str: str) -> datetime:
    """Разбирает строку временной метки в объект datetime."""
    try:
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        raise InvalidTimestampError(f"Неверная временная метка: {ts_str}")


def validate_event(data: dict, line_num: int, file_name: str) -> Event:
    """Проверяет обязательные поля и типы данных."""
    required_fields = ["timestamp", "level", "source", "message"]
    for field in required_fields:
        if field not in data:
            raise InvalidEventError(f"Файл {file_name}, строка {line_num}: отсутствует поле '{field}'")

    if not isinstance(data["source"], str) or not data["source"].strip():
        raise InvalidEventError(f"Файл {file_name}, строка {line_num}: source должен быть непустой строкой")

    if not isinstance(data["message"], str):
        raise InvalidEventError(f"Файл {file_name}, строка {line_num}: message должен быть строкой")

    if data["level"] not in VALID_LEVELS:
        raise InvalidEventError(f"Файл {file_name}, строка {line_num}: неверный level '{data['level']}'")

    ts = parse_timestamp(data["timestamp"])

    return Event(
        timestamp=ts,
        level=data["level"],
        source=data["source"],
        message=str(data["message"])
    )