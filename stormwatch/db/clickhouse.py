import json
from datetime import datetime
from uuid import uuid4

import clickhouse_connect

from config import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_PORT,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
    CLICKHOUSE_SECURE,
)


_client = None


def get_client():
    global _client
    if _client is None:
        _client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            secure=CLICKHOUSE_SECURE,
        )
    return _client


def query(sql: str, params: dict | None = None) -> list[dict]:
    client = get_client()
    result = client.query(sql, parameters=params)
    columns = result.column_names
    return [dict(zip(columns, row)) for row in result.result_rows]


def command(sql: str):
    client = get_client()
    client.command(sql)


def insert(table: str, data: list[dict]):
    if not data:
        return
    client = get_client()
    rows = [list(row.values()) for row in data]
    columns = list(data[0].keys())
    client.insert(table, rows, column_names=columns)


def insert_weather_events(events: list[dict]):
    if not events:
        return
    client = get_client()
    rows = []
    for e in events:
        rows.append([
            e.get("event_id", str(uuid4())),
            e.get("timestamp", datetime.utcnow()),
            e["latitude"],
            e["longitude"],
            e["event_type"],
            e["severity"],
            e.get("wind_speed_kmh", 0.0),
            e.get("precipitation_mm", 0.0),
            e.get("description", ""),
            e.get("source", "simulated"),
        ])
    client.insert(
        "weather_events",
        rows,
        column_names=[
            "event_id", "timestamp", "latitude", "longitude",
            "event_type", "severity", "wind_speed_kmh",
            "precipitation_mm", "description", "source",
        ],
    )
