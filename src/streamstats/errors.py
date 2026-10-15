class StreamStatsError(Exception):
    """Базовый класс для всех ошибок streamstats."""

class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат файла."""

class InvalidEventError(StreamStatsError):
    """Ошибка валидации события."""

class InvalidTimestampError(StreamStatsError):
    """Неверная временная метка."""

class CLIConfigError(StreamStatsError):
    """Ошибка конфигурации CLI."""
