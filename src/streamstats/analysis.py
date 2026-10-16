from collections import defaultdict

from .models import Event


class StatsAggregator:
    """Накопитель статистики событиЙ."""
    def __init__(self):
        """Инициализирует агрегатор нулевыми значениями."""
        self.total_events = 0
        self.levels = defaultdict(int)
        self.sources = defaultdict(int)
        self.error_sources = defaultdict(int)
        self.first_ts = None
        self.last_ts = None
        self.skipped_lines = 0

    def add_event(self, event: Event):
        """Добавляет событие в агрегатор."""
        self.total_events += 1
        self.levels[event.level] += 1
        self.sources[event.source] += 1
        if event.level in ("ERROR", "CRITICAL"):
            self.error_sources[event.source] += 1
        if self.first_ts is None or event.timestamp < self.first_ts:
            self.first_ts = event.timestamp
        if self.last_ts is None or event.timestamp > self.last_ts:
            self.last_ts = event.timestamp

    def get_top_error_sources(self, n=5):
        """Возвращает топ-5 источников по количеству ошибок."""
        sorted_sources = sorted(self.error_sources.items(), key=lambda x: (-x[1], x[0]))
        return [{"source": src, "count": cnt} for src, cnt in sorted_sources[:n]]