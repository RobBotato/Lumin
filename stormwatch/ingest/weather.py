import asyncio
import random
from datetime import datetime
from uuid import uuid4

from config import DEMO_MODE, OWM_API_KEY
from db.clickhouse import insert_weather_events


MONITOR_COORDS = [
    (14.5, 119.0, "South China Sea"),
    (21.0, 121.5, "Luzon Strait"),
    (2.5, 102.0, "Malacca Strait"),
    (8.0, 76.0, "Indian Ocean N"),
    (18.0, 40.0, "Red Sea"),
    (36.0, 15.0, "Mediterranean"),
    (45.0, -35.0, "North Atlantic"),
    (26.0, -90.0, "Gulf of Mexico"),
    (-20.0, -30.0, "South Atlantic"),
    (-22.0, 155.0, "Coral Sea"),
]

DEMO_SCENARIOS = [
    {
        "trigger_cycle": 4,
        "lat": 14.5, "lon": 119.0,
        "type": "storm",
        "severity": "severe",
        "wind": 177,
        "precip": 85,
        "desc": (
            "Tropical Storm Mara, Category 2, expected to make landfall "
            "near Manila with sustained winds of 110 mph, affecting "
            "shipping lanes in the South China Sea through Thursday."
        ),
    },
    {
        "trigger_cycle": 10,
        "lat": 22.0, "lon": 115.0,
        "type": "hurricane",
        "severity": "extreme",
        "wind": 220,
        "precip": 140,
        "desc": (
            "Typhoon Kirogi intensifying to Category 4 with sustained "
            "winds of 140 mph. Storm track headed toward Hong Kong "
            "and Shenzhen ports. Expected to cross major Pacific "
            "shipping corridors within 24 hours."
        ),
    },
]


async def poll(demo: bool = True, cycle: int = 1) -> list[dict]:
    if demo:
        return _demo_poll(cycle)

    if OWM_API_KEY:
        return await _live_poll()
    return []


def _demo_poll(cycle: int) -> list[dict]:
    events = []

    for scenario in DEMO_SCENARIOS:
        if scenario["trigger_cycle"] <= cycle <= scenario["trigger_cycle"] + 5:
            events.append({
                "event_id": str(uuid4()),
                "timestamp": datetime.utcnow(),
                "latitude": scenario["lat"],
                "longitude": scenario["lon"],
                "event_type": scenario["type"],
                "severity": scenario["severity"],
                "wind_speed_kmh": scenario["wind"],
                "precipitation_mm": scenario["precip"],
                "description": scenario["desc"],
                "source": "simulated",
            })

    # Add calm weather for remaining coords
    for lat, lon, name in MONITOR_COORDS:
        if random.random() < 0.8:
            events.append({
                "event_id": str(uuid4()),
                "timestamp": datetime.utcnow(),
                "latitude": lat,
                "longitude": lon,
                "event_type": "clear",
                "severity": "low",
                "wind_speed_kmh": random.uniform(5, 30),
                "precipitation_mm": random.uniform(0, 5),
                "description": f"Calm conditions in {name}.",
                "source": "simulated",
            })

    return events


async def _live_poll() -> list[dict]:
    try:
        import httpx
        events = []
        async with httpx.AsyncClient(timeout=10) as client:
            for lat, lon, _name in MONITOR_COORDS:
                try:
                    resp = await client.get(
                        "https://api.openweathermap.org/data/2.5/weather",
                        params={
                            "lat": lat, "lon": lon,
                            "appid": OWM_API_KEY,
                            "units": "metric",
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        severity = _map_owm_severity(data)
                        events.append({
                            "event_id": str(uuid4()),
                            "timestamp": datetime.utcnow(),
                            "latitude": lat,
                            "longitude": lon,
                            "event_type": _map_owm_type(data),
                            "severity": severity,
                            "wind_speed_kmh": data.get("wind", {}).get("speed", 0) * 3.6,
                            "precipitation_mm": data.get("rain", {}).get("1h", 0),
                            "description": _build_owm_desc(data),
                            "source": "openweathermap",
                        })
                except Exception:
                    continue
        return events
    except ImportError:
        return []


def _map_owm_severity(data: dict) -> str:
    wind = data.get("wind", {}).get("speed", 0) * 3.6
    weather = data.get("weather", [{}])[0].get("main", "").lower()
    if weather in ("thunderstorm", "hurricane", "tornado") or wind > 118:
        return "extreme"
    if weather in ("rain", "snow") or wind > 62:
        return "severe"
    if wind > 30 or weather in ("drizzle",):
        return "moderate"
    return "low"


def _map_owm_type(data: dict) -> str:
    weather = data.get("weather", [{}])[0].get("main", "").lower()
    mapping = {
        "thunderstorm": "storm", "hurricane": "hurricane",
        "tornado": "storm", "rain": "flood", "snow": "winter_storm",
        "fog": "fog", "mist": "fog",
    }
    return mapping.get(weather, "clear")


def _build_owm_desc(data: dict) -> str:
    w = data.get("weather", [{}])[0]
    desc = w.get("description", "No details")
    wind = data.get("wind", {}).get("speed", 0) * 3.6
    return f"{desc}. Wind: {wind:.0f} km/h."


async def run():
    while True:
        events = await poll()
        if events:
            insert_weather_events(events)
        await asyncio.sleep(30)
