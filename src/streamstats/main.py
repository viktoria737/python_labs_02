import argparse
import logging
import sys
from pathlib import Path

from .analysis import StatsAggregator
from .errors import CLIConfigError, StreamStatsError
from .parsers import parse_file
from .report import generate_report


def setup_logger():
    """Настраивает логгер для вывода в stdout."""
    logger = logging.getLogger("streamstats")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for old_handler in logger.handlers[:]:
        logger.removeHandler(old_handler)
        old_handler.close()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def main():
    """Главная функция CLI.
    Парсит аргументы, обрабатывает файлы и генерирует отчёт."""
    logger = setup_logger()

    parser = argparse.ArgumentParser(prog="streamstats", description="Stream Analyzer")
    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser("analyze", help="Анализ логов")
    analyze_parser.add_argument("inputs", nargs="+", type=Path, help="Входные файлы")
    analyze_parser.add_argument("--format", required=True, choices=["csv", "jsonl"], help="Формат файлов")
    analyze_parser.add_argument("--output", required=True, help="Путь к JSON-отчету")
    analyze_parser.add_argument("--skip-invalid", action="store_true", help="Пропускать битые строки")

    args = parser.parse_args()

    if args.command != "analyze":
        parser.print_help()
        sys.exit(1)

    aggregator = StatsAggregator()

    try:
        for input_file in args.inputs:
            if not input_file.exists():
                raise CLIConfigError(f"Файл не найден: {input_file}")

            logger.info(f"Начинается обработка файла {input_file}")

            for item, line_num in parse_file(input_file, args.format):
                if isinstance(item, StreamStatsError):
                    if args.skip_invalid:
                        logger.warning(f"В строке {line_num} пропущено: {item}")
                        aggregator.skipped_lines += 1
                    else:
                        logger.error(f"Ошибка в файле {input_file}, строка {line_num}: {item}")
                        sys.exit(2)
                else:
                    aggregator.add_event(item)

        generate_report(aggregator, args.output)
        logger.info(f"Отчет сохранен в {args.output}")

    except StreamStatsError as e:
        logger.error(str(e))
        sys.exit(2)
    except Exception as e: # noqa: BLE001 - последний catch-all для CLI
        logger.error(f"Непредвиденная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()