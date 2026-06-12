from db.clickhouse import command


SQL_CREATE_WEATHER_EVENTS = """
CREATE TABLE IF NOT EXISTS weather_events (
    event_id String,
    timestamp DateTime,
    latitude Float64,
    longitude Float64,
    event_type String,
    severity String,
    wind_speed_kmh Float32,
    precipitation_mm Float32,
    description String,
    source String
) ENGINE = MergeTree()
ORDER BY (timestamp, event_type, severity)
"""

SQL_CREATE_SHIPPING_ROUTES = """
CREATE TABLE IF NOT EXISTS shipping_routes (
    route_id String,
    vessel_name String,
    origin_port String,
    destination_port String,
    waypoint_lat Float64,
    waypoint_lon Float64,
    waypoint_order UInt8,
    cargo_value_usd UInt64,
    eta DateTime,
    status String
) ENGINE = MergeTree()
ORDER BY (route_id, waypoint_order)
"""

SQL_CREATE_PORTS = """
CREATE TABLE IF NOT EXISTS ports (
    port_code String,
    port_name String,
    latitude Float64,
    longitude Float64,
    country String,
    weather_vulnerability Float32
) ENGINE = MergeTree()
ORDER BY port_code
"""

SQL_CREATE_RISK_ASSESSMENTS = """
CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id String,
    timestamp DateTime,
    weather_event_id String,
    affected_routes Array(String),
    risk_level String,
    estimated_delay_hours UInt16,
    financial_impact_usd UInt64,
    recommendation String,
    langfuse_trace_id String
) ENGINE = MergeTree()
ORDER BY (timestamp, risk_level)
"""

SQL_CREATE_HISTORICAL_DISRUPTIONS = """
CREATE TABLE IF NOT EXISTS historical_disruptions (
    disruption_id String,
    event_name String,
    event_type String,
    region String,
    avg_delay_days Float32,
    estimated_cost_usd UInt64,
    ports_affected Array(String),
    lessons String
) ENGINE = MergeTree()
ORDER BY (event_type, region)
"""

TABLES = [
    ("weather_events", SQL_CREATE_WEATHER_EVENTS),
    ("shipping_routes", SQL_CREATE_SHIPPING_ROUTES),
    ("ports", SQL_CREATE_PORTS),
    ("risk_assessments", SQL_CREATE_RISK_ASSESSMENTS),
    ("historical_disruptions", SQL_CREATE_HISTORICAL_DISRUPTIONS),
]


def create_all_tables():
    for name, sql in TABLES:
        try:
            command(sql)
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
