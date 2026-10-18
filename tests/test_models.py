import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import parse_timestamp, validate_event


def test_parse_timestamp_valid():
    """Проверяет корректный парсинг валидной временной метки."""
    dt = parse_timestamp("2026-10-07T12:00:00+03:00")
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 7
    assert dt.hour == 12


def test_parse_timestamp_invalid():
    """Проверяет выброс InvalidTimestampError для неверного формата."""
    with pytest.raises(InvalidTimestampError):
        parse_timestamp("not-a-date")


def test_validate_event_ok():
    """Проверяет создание валидного события."""
    data = {
        "timestamp": "2026-10-07T12:00:00+03:00",
        "level": "INFO",
        "source": "app",
        "message": "ok",
    }
    event = validate_event(data, 1, "test.jsonl")
    assert event.level == "INFO"
    assert event.source == "app"
    assert event.message == "ok"


def test_validate_event_missing_field():
    """Проверяет ошибку при отсутствии обязательного поля."""
    data = {"timestamp": "2026-10-07T12:00:00+03:00", "level": "INFO"}
    with pytest.raises(InvalidEventError):
        validate_event(data, 5, "test.jsonl")


def test_validate_event_empty_source():
    """Проверяет ошибку при пустом source."""
    data = {
        "timestamp": "2026-10-07T12:00:00+03:00",
        "level": "INFO",
        "source": "",
        "message": "ok",
    }
    with pytest.raises(InvalidEventError):
        validate_event(data, 1, "test.jsonl")


def test_validate_event_bad_level():
    """Проверяет ошибку при недопустимом уровне."""
    data = {
        "timestamp": "2026-10-07T12:00:00+03:00",
        "level": "TRACE",
        "source": "app",
        "message": "ok",
    }
    with pytest.raises(InvalidEventError):
        validate_event(data, 1, "test.jsonl")