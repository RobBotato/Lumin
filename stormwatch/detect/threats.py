from db.clickhouse import query

THREAT_DETECTION_SQL = """
WITH threats AS (
    SELECT
        w.event_id,
        w.event_type,
        w.severity,
        w.latitude AS storm_lat,
        w.longitude AS storm_lon,
        w.description,
        w.wind_speed_kmh,
        w.precipitation_mm,
        r.route_id,
        r.vessel_name,
        r.cargo_value_usd,
        r.waypoint_lat,
        r.waypoint_lon,
        r.destination_port,
        111.045 * sqrt(
            pow(w.latitude - r.waypoint_lat, 2) +
            pow((w.longitude - r.waypoint_lon) * cos(w.latitude * pi() / 180), 2)
        ) AS distance_km
    FROM weather_events w
    CROSS JOIN shipping_routes r
    WHERE w.timestamp > now() - INTERVAL 6 HOUR
        AND w.severity IN ('severe', 'extreme')
        AND r.status = 'in_transit'
)
SELECT *
FROM threats
WHERE distance_km < 300
ORDER BY distance_km ASC
"""

HISTORICAL_PATTERN_SQL = """
SELECT
    event_name,
    event_type,
    region,
    avg_delay_days,
    estimated_cost_usd,
    ports_affected,
    lessons
FROM historical_disruptions
WHERE event_type = {event_type:String}
    AND region = {region:String}
ORDER BY estimated_cost_usd DESC
LIMIT 5
"""

ROUTE_IMPACT_SQL = """
SELECT
    count(DISTINCT route_id) AS routes_affected,
    sum(cargo_value_usd) AS total_cargo_at_risk,
    groupArray(vessel_name) AS vessels,
    groupArray(destination_port) AS destinations
FROM shipping_routes
WHERE route_id IN ({route_ids:Array(String)})
    AND status = 'in_transit'
"""

REGION_MAP = {
    (10, 25, 110, 130): "South China Sea",
    (-30, 5, 30, 100): "Indian Ocean",
    (25, 40, -100, -80): "Gulf of Mexico",
    (40, 55, -40, 10): "North Atlantic",
    (15, 25, 35, 45): "Red Sea",
}


def scan_threats() -> list[dict]:
    try:
        return query(THREAT_DETECTION_SQL)
    except Exception as e:
        print(f"Threat scan error: {e}")
        return []


def get_historical_matches(event_type: str, region: str) -> list[dict]:
    if not event_type:
        return []
    try:
        return query(HISTORICAL_PATTERN_SQL, {
            "event_type": event_type,
            "region": region,
        })
    except Exception:
        return []


def get_route_impact(route_ids: list[str]) -> dict | None:
    if not route_ids:
        return None
    try:
        results = query(ROUTE_IMPACT_SQL, {"route_ids": route_ids})
        return results[0] if results else None
    except Exception:
        return None


def resolve_region(lat: float, lon: float) -> str:
    for (lat_min, lat_max, lon_min, lon_max), name in REGION_MAP.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return name
    return "Unknown"
