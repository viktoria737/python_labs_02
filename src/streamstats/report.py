import json

from .analysis import StatsAggregator


def generate_report(aggregator: StatsAggregator, output_path: str):
    """Формирует и записывает JSON-отчёт."""
    report = {
        "total_events": aggregator.total_events,
        "levels": dict(aggregator.levels),
        "sources": dict(aggregator.sources),
        "top_error_sources": aggregator.get_top_error_sources(),
        "first_timestamp": aggregator.first_ts.isoformat() if aggregator.first_ts else None,
        "last_timestamp": aggregator.last_ts.isoformat() if aggregator.last_ts else None,
        "skipped_lines": aggregator.skipped_lines
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)