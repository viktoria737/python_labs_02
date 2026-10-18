import pytest

from streamstats.errors import InvalidEventError, UnsupportedFormatError
from streamstats.models import Event
from streamstats.parsers import parse_file


def test_jsonl_valid(tmp_path):
    """Проверяет парсинг валидного JSONL-файла."""
    file = tmp_path / "log.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-07T12:00:00+03:00", "level": "INFO", '
        '"source": "app", "message": "start"}\n',
        encoding="utf-8",
    )
    events = list(parse_file(file, "jsonl"))
    assert len(events) == 1
    event, line_num = events[0]
    assert isinstance(event, Event)
    assert event.source == "app"
    assert line_num == 1


def test_jsonl_empty_file(tmp_path):
    """Проверяет обработку пустого JSONL-файла."""
    file = tmp_path / "empty.jsonl"
    file.write_text("", encoding="utf-8")
    events = list(parse_file(file, "jsonl"))
    assert events == []


def test_jsonl_broken_line_default(tmp_path):
    """Проверяет возврат ошибки для невалидной JSON-строки."""
    file = tmp_path / "broken.jsonl"
    file.write_text("not a json\n", encoding="utf-8")
    events = list(parse_file(file, "jsonl"))
    assert len(events) == 1
    result, line_num = events[0]
    assert isinstance(result, InvalidEventError)
    assert line_num == 1


def test_jsonl_unicode(tmp_path):
    """Проверяет поддержку Unicode в JSONL."""
    file = tmp_path / "uni.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-07T12:00:00+03:00", "level": "INFO", '
        '"source": "сервер", "message": "Привет, мир!"}\n',
        encoding="utf-8",
    )
    events = list(parse_file(file, "jsonl"))
    assert len(events) == 1
    event, _line_num = events[0]
    assert isinstance(event, Event)
    assert event.message == "Привет, мир!"
    assert event.source == "сервер"


def test_csv_valid(tmp_path):
    """Проверяет парсинг валидного CSV-файла."""
    file = tmp_path / "log.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-07T12:00:00+03:00,ERROR,db,timeout\n",
        encoding="utf-8",
    )
    events = list(parse_file(file, "csv"))
    assert len(events) == 1
    event, _line_num = events[0]
    assert isinstance(event, Event)
    assert event.level == "ERROR"


def test_csv_empty_file(tmp_path):
    """Проверяет обработку пустого CSV-файла."""
    file = tmp_path / "empty.csv"
    file.write_text("", encoding="utf-8")
    events = list(parse_file(file, "csv"))
    assert events == []


def test_unsupported_format(tmp_path):
    """Проверяет ошибку для неподдерживаемого формата."""
    file = tmp_path / "log.xml"
    file.write_text("<root/>", encoding="utf-8")
    with pytest.raises(UnsupportedFormatError):
        list(parse_file(file, "xml"))