# Потоковый анализатор файлов.

Пакет `streamstats`, читающий события из CSV и JSONL файлов и создающий статистический отчёт.

## Функциональность

* Чтение входных файлов построчно.
* Не используется `read()` без ограничения и `readlines()` для всего файла.
* Поддержка CSV с заголовком и JSONL.
* Валидация обязательных полей.
* Агрегация статистики по уровням и источникам.
* Выводится топ-5 источников ошибок уровня ERROR/CRITICAL. 
* Находится первая и последняя временная метка.
* Формируется JSON-отчёт.
* Объединяется статистика нескольких файлов.

## Ошибки

* Неподдерживаемый формат.
* Неверное событие.
* Неверная временная метка.
* Ошибка конфигурации CLI.

#### При встрече ошибочной строки:
Режим по умолчанию:
* останавливается обработка;
* выводится сообщение об ошибке с именем файла и номером строк;
* CLI завершается с кодом `2`.

Режим `--skip-invalid`:
* ошибочная строка пропускается;
* в лог выводится WARNING;
* в отчёт добавляется количество пропущенных строк.

## Установка

Создание виртуального окружения:

```bash
python -m venv .venv
```

Активация окружения:

```bash
#Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\Activate.ps1
```

Установка пакета и инструментов для проверки:

```bash
pip install -e .
pip install pytest ruff
```

## Использование

```bash
# Анализ одного JSONL-файла
python -m streamstats analyze INPUT --format jsonl --output REPORT.json

# Анализ одного CSV-файла
python -m streamstats analyze INPUT --format csv --output REPORT.json

# Анализ нескольких файлов
python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output REPORT.json

# Пропуск ошибочных строк
python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output REPORT.json --skip-invalid

# Справка
python -m streamstats --help
```

## Структура отчёта

```bash
{
  "total_events": 150,
  "levels": {
    "INFO": 100,
    "WARNING": 30,
    "ERROR": 15,
    "CRITICAL": 5
  },
  "sources": {
    "loader": 50,
    "db": 80,
    "cache": 20
  },
  "top_error_sources": [
    {"source": "db", "count": 20},
    {"source": "cache", "count": 5}
  ],
  "first_timestamp": "2026-10-07T12:00:00+03:00",
  "last_timestamp": "2026-10-07T18:30:00+03:00",
  "skipped_lines": 3
}
```

| Поле                | Описание                               |
|---------------------|----------------------------------------|
| `total_events`      | Общее количество валидных событий      |
| `levels`            | Распределение событий по уровням       |
| `sources`           | Распределение событий по источникам    |
| `top_error_sources` | Топ-5 источников ошибок                |
| `first_timestamp`   | Самая ранняя временная метка           |
| `last_timestamp`    | Самая поздняя временная метка          |
| `skipped_lines`     | Количество пропущенных ошибочных строк |


## Структура проекта

```text
lab_02/
|── src/
|   └── streamstats/
|       |── __init__.py       # инициализация пакета
|       |── __main__.py       # точка входа
|       |── analysis.py       # агрегация статистики
|       |── errors.py         # классы ошибок
|       |── main.py           # CLI-интерфейс
|       |── models.py         # валидация
|       |── parsers.py        # потоковые парсеры CSV и JSONL
|       └── report.py         # генерация JSON-отчёта
|
|── tests/
|   |── __init__.py
|   |── test_analysis.py      # тесты агрегации
|   |── test_cli.py           # тесты для командного интерфейса (CLI)
|   |── test_models.py        # тесты валидации
|   └── test_parsers.py       # Unit-тесты парсеров
|
|── .gitignore                # исключения для Git
|── pyproject.toml            # конфигурация проекта
└── README.md                 # документация проекта

```