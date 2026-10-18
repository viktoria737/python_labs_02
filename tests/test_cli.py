import json
import subprocess
import sys


def run(*args, cwd=None):
    """Запускает python -m streamstats с заданными аргументами."""
    cmd = [sys.executable, "-m", "streamstats"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        check=False,
        text=True,
        cwd=cwd,
    )


def test_cli_analyze_jsonl(tmp_path):
    """Анализ одного JSONL-файла."""
    log = tmp_path / "log.jsonl"
    log.write_text(
        '{"timestamp": "2026-10-07T12:00:00+03:00", "level": "INFO", '
        '"source": "app", "message": "ok"}\n'
        '{"timestamp": "2026-10-07T12:05:00+03:00", "level": "ERROR", '
        '"source": "db", "message": "fail"}\n',
        encoding="utf-8",
    )
    report = tmp_path / "report.json"

    result = run(
        "analyze", str(log),
        "--format", "jsonl",
        "--output", str(report),
    )

    assert result.returncode == 0, result.stderr
    assert report.exists()
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["levels"]["ERROR"] == 1
    assert data["top_error_sources"][0]["source"] == "db"


def test_cli_multiple_files(tmp_path):
    """Проверяет объединение статистики из нескольких файлов."""
    f1 = tmp_path / "a.jsonl"
    f2 = tmp_path / "b.jsonl"
    f1.write_text(
        '{"timestamp": "2026-10-07T12:00:00+03:00", "level": "INFO", '
        '"source": "app", "message": "x"}\n',
        encoding="utf-8",
    )
    f2.write_text(
        '{"timestamp": "2026-10-07T13:00:00+03:00", "level": "WARNING", '
        '"source": "app", "message": "y"}\n',
        encoding="utf-8",
    )
    report = tmp_path / "report.json"

    result = run(
        "analyze", str(f1), str(f2),
        "--format", "jsonl",
        "--output", str(report),
    )
    assert result.returncode == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["sources"]["app"] == 2


def test_cli_broken_line_default_exit_code(tmp_path):
    """Проверяет код возврата 2 при битой строке"""
    log = tmp_path / "broken.jsonl"
    log.write_text("not a json\n", encoding="utf-8")
    report = tmp_path / "report.json"

    result = run(
        "analyze", str(log),
        "--format", "jsonl",
        "--output", str(report),
    )
    assert result.returncode == 2


def test_cli_skip_invalid(tmp_path):
    """Проверяет пропуск битых строк с флагом --skip-invalid."""
    log = tmp_path / "mixed.jsonl"
    log.write_text(
        '{"timestamp": "2026-10-07T12:00:00+03:00", "level": "INFO", '
        '"source": "app", "message": "ok"}\n'
        "not a json\n"
        '{"timestamp": "2026-10-07T12:05:00+03:00", "level": "ERROR", '
        '"source": "db", "message": "fail"}\n',
        encoding="utf-8",
    )
    report = tmp_path / "report.json"

    result = run(
        "analyze", str(log),
        "--format", "jsonl",
        "--output", str(report),
        "--skip-invalid",
    )
    assert result.returncode == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["total_events"] == 2
    assert data["skipped_lines"] == 1