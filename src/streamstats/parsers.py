import csv
import json
from collections.abc import Generator
from pathlib import Path

from .errors import InvalidEventError, UnsupportedFormatError
from .models import Event, validate_event


def parse_file(
        file_path: Path, fmt: str
) -> Generator[tuple[Event | InvalidEventError, int], None, None]:
    """Потоковый парсер файла.
    Читает файл построчно и возвращает генератор кортежей."""
    if fmt == "csv":
        yield from parse_csv(file_path)
    elif fmt == "jsonl":
        yield from parse_jsonl(file_path)
    else:
        raise UnsupportedFormatError(f"Формат '{fmt}' не поддерживается")


def parse_csv(file_path: Path):
    """Парсер CSV-файла с заголовком."""
    with file_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                event = validate_event(row, reader.line_num, file_path.name)
                yield event, reader.line_num
            except InvalidEventError as e:
                yield e, reader.line_num


def parse_jsonl(file_path: Path):
    """Парсер JSONL-файла."""
    with file_path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                yield InvalidEventError(
                    f"Файл {file_path.name}, строка {line_num}: невалидный JSON"
                ), line_num
                continue
            try:
                event = validate_event(data, line_num, file_path.name)
                yield event, line_num
            except InvalidEventError as e:
                yield e, line_num