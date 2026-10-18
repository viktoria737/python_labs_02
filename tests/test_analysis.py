from datetime import datetime

from streamstats.analysis import StatsAggregator
from streamstats.models import Event


def _event(ts, level, source):
    """Вспомогательная функция создания тестового события."""
    return Event(
        timestamp=datetime.fromisoformat(ts),
        level=level,
        source=source,
        message="x",
    )


def test_aggregator_counts():
    """Проверяет подсчёт событий и распределение по уровням."""
    agg = StatsAggregator()
    agg.add_event(_event("2026-10-07T12:00:00+03:00", "INFO", "app"))
    agg.add_event(_event("2026-10-07T12:05:00+03:00", "ERROR", "db"))
    agg.add_event(_event("2026-10-07T12:10:00+03:00", "ERROR", "db"))
    agg.add_event(_event("2026-10-07T12:15:00+03:00", "CRITICAL", "cache"))
    assert agg.total_events == 4
    assert agg.levels["ERROR"] == 2
    assert agg.sources["db"] == 2
    assert agg.first_ts < agg.last_ts


def test_top_error_sources():
    """Проверяет сортировку источников ошибок."""
    agg = StatsAggregator()
    agg.add_event(_event("2026-10-07T12:00:00+03:00", "ERROR", "b"))
    agg.add_event(_event("2026-10-07T12:01:00+03:00", "ERROR", "b"))
    agg.add_event(_event("2026-10-07T12:02:00+03:00", "ERROR", "a"))
    agg.add_event(_event("2026-10-07T12:03:00+03:00", "ERROR", "a"))
    agg.add_event(_event("2026-10-07T12:04:00+03:00", "ERROR", "c"))
    top = agg.get_top_error_sources(2)
    assert top[0]["source"] == "a"
    assert top[0]["count"] == 2
    assert top[1]["source"] == "b"
    assert len(top) == 2