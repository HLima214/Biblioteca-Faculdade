"""Funções de data/hora (sempre em UTC)."""
from datetime import datetime, timezone


def agora():
    return datetime.now(timezone.utc)


def como_utc(dt):
    """Garante um datetime com fuso UTC (evita erro ao comparar datas)."""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
