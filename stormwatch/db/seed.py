from datetime import datetime, timedelta
from uuid import uuid4

from db.clickhouse import insert


def seed_shipping_routes():
    now = datetime.utcnow()
    routes = [
        {
            "route_id": "SHA-LAX-01",
            "vessel_name": "MV Pacific Dawn",
            "origin_port": "Shanghai",
            "destination_port": "Los Angeles",
            "waypoint_lat": 31.23,
            "waypoint_lon": 121.47,
            "waypoint_order": 0,
            "cargo_value_usd": 12_000_000,
            "eta": now + timedelta(days=12),
            "status": "in_transit",
        },
        # Add waypoints for SHA-LAX-01 (Pacific crossing)
        *[
            {
                "route_id": "SHA-LAX-01",
                "vessel_name": "MV Pacific Dawn",
                "origin_port": "Shanghai",
                "destination_port": "Los Angeles",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 12_000_000,
                "eta": now + timedelta(days=12),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (28.0, 125.0), (22.0, 130.0), (18.0, 140.0),
                (22.0, 150.0), (30.0, 160.0), (38.0, 170.0),
                (35.0, -150.0), (33.0, -130.0), (33.5, -120.0),
            ], start=1)
        ],
        {
            "route_id": "RTM-SGP-02",
            "vessel_name": "MV Europa Star",
            "origin_port": "Rotterdam",
            "destination_port": "Singapore",
            "waypoint_lat": 51.91,
            "waypoint_lon": 4.48,
            "waypoint_order": 0,
            "cargo_value_usd": 8_500_000,
            "eta": now + timedelta(days=20),
            "status": "in_transit",
        },
        *[
            {
                "route_id": "RTM-SGP-02",
                "vessel_name": "MV Europa Star",
                "origin_port": "Rotterdam",
                "destination_port": "Singapore",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 8_500_000,
                "eta": now + timedelta(days=20),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (48.0, -5.0), (36.0, -5.0), (31.0, 32.0),
                (12.0, 44.0), (6.0, 55.0), (3.0, 78.0),
                (1.5, 90.0), (1.2, 100.0), (1.26, 103.8),
            ], start=1)
        ],
        {
            "route_id": "SGP-SYD-03",
            "vessel_name": "MV Southern Cross",
            "origin_port": "Singapore",
            "destination_port": "Sydney",
            "waypoint_lat": 1.26,
            "waypoint_lon": 103.84,
            "waypoint_order": 0,
            "cargo_value_usd": 5_200_000,
            "eta": now + timedelta(days=8),
            "status": "in_transit",
        },
        *[
            {
                "route_id": "SGP-SYD-03",
                "vessel_name": "MV Southern Cross",
                "origin_port": "Singapore",
                "destination_port": "Sydney",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 5_200_000,
                "eta": now + timedelta(days=8),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (-2.0, 105.0), (-6.0, 110.0), (-10.0, 120.0),
                (-15.0, 130.0), (-20.0, 140.0), (-25.0, 148.0),
                (-30.0, 151.0), (-33.0, 151.2),
            ], start=1)
        ],
        {
            "route_id": "HKG-LAX-04",
            "vessel_name": "MV Orient Express",
            "origin_port": "Hong Kong",
            "destination_port": "Los Angeles",
            "waypoint_lat": 22.29,
            "waypoint_lon": 114.16,
            "waypoint_order": 0,
            "cargo_value_usd": 15_000_000,
            "eta": now + timedelta(days=14),
            "status": "in_transit",
        },
        *[
            {
                "route_id": "HKG-LAX-04",
                "vessel_name": "MV Orient Express",
                "origin_port": "Hong Kong",
                "destination_port": "Los Angeles",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 15_000_000,
                "eta": now + timedelta(days=14),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (20.0, 120.0), (18.0, 130.0), (22.0, 145.0),
                (28.0, 160.0), (35.0, 175.0), (38.0, -160.0),
                (35.0, -140.0), (33.5, -125.0), (33.7, -118.3),
            ], start=1)
        ],
        {
            "route_id": "SHZ-MNL-06",
            "vessel_name": "MV Pearl River",
            "origin_port": "Shenzhen",
            "destination_port": "Manila",
            "waypoint_lat": 22.54,
            "waypoint_lon": 113.93,
            "waypoint_order": 0,
            "cargo_value_usd": 3_800_000,
            "eta": now + timedelta(days=3),
            "status": "in_transit",
        },
        *[
            {
                "route_id": "SHZ-MNL-06",
                "vessel_name": "MV Pearl River",
                "origin_port": "Shenzhen",
                "destination_port": "Manila",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 3_800_000,
                "eta": now + timedelta(days=3),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (20.0, 116.0), (18.0, 118.0), (16.0, 119.0),
                (14.6, 120.9),
            ], start=1)
        ],
        {
            "route_id": "JED-RTM-05",
            "vessel_name": "MV Arabian Sea",
            "origin_port": "Jeddah",
            "destination_port": "Rotterdam",
            "waypoint_lat": 21.49,
            "waypoint_lon": 39.19,
            "waypoint_order": 0,
            "cargo_value_usd": 22_000_000,
            "eta": now + timedelta(days=16),
            "status": "in_transit",
        },
        *[
            {
                "route_id": "JED-RTM-05",
                "vessel_name": "MV Arabian Sea",
                "origin_port": "Jeddah",
                "destination_port": "Rotterdam",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 22_000_000,
                "eta": now + timedelta(days=16),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (25.0, 35.0), (31.0, 32.0), (36.0, 15.0),
                (38.0, 0.0), (43.0, -10.0), (48.0, -5.0),
                (50.0, 0.0), (51.5, 2.0), (51.9, 4.48),
            ], start=1)
        ],
        {
            "route_id": "BUE-HOU-07",
            "vessel_name": "MV Southern Tide",
            "origin_port": "Buenos Aires",
            "destination_port": "Houston",
            "waypoint_lat": -34.61,
            "waypoint_lon": -58.37,
            "waypoint_order": 0,
            "cargo_value_usd": 7_100_000,
            "eta": now + timedelta(days=15),
            "status": "in_transit",
        },
        *[
            {
                "route_id": "BUE-HOU-07",
                "vessel_name": "MV Southern Tide",
                "origin_port": "Buenos Aires",
                "destination_port": "Houston",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 7_100_000,
                "eta": now + timedelta(days=15),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (-30.0, -50.0), (-20.0, -40.0), (-5.0, -35.0),
                (5.0, -45.0), (15.0, -65.0), (22.0, -80.0),
                (25.0, -88.0), (29.0, -93.0), (29.75, -95.3),
            ], start=1)
        ],
        {
            "route_id": "MUM-DUR-08",
            "vessel_name": "MV Indian Monarch",
            "origin_port": "Mumbai",
            "destination_port": "Durban",
            "waypoint_lat": 18.93,
            "waypoint_lon": 72.84,
            "waypoint_order": 0,
            "cargo_value_usd": 6_400_000,
            "eta": now + timedelta(days=11),
            "status": "in_transit",
        },
        *[
            {
                "route_id": "MUM-DUR-08",
                "vessel_name": "MV Indian Monarch",
                "origin_port": "Mumbai",
                "destination_port": "Durban",
                "waypoint_lat": lat,
                "waypoint_lon": lon,
                "waypoint_order": i,
                "cargo_value_usd": 6_400_000,
                "eta": now + timedelta(days=11),
                "status": "in_transit",
            }
            for i, (lat, lon) in enumerate([
                (15.0, 70.0), (8.0, 60.0), (0.0, 50.0),
                (-10.0, 40.0), (-20.0, 35.0), (-25.0, 33.0),
                (-29.0, 31.0),
            ], start=1)
        ],
    ]
    insert("shipping_routes", routes)
    print(f"  ✓ shipping_routes ({len(routes)} rows)")


def seed_ports():
    ports = [
        {"port_code": "CNSHA", "port_name": "Shanghai", "latitude": 31.23, "longitude": 121.47, "country": "CN", "weather_vulnerability": 0.65},
        {"port_code": "SGSIN", "port_name": "Singapore", "latitude": 1.26, "longitude": 103.84, "country": "SG", "weather_vulnerability": 0.30},
        {"port_code": "NLRTM", "port_name": "Rotterdam", "latitude": 51.91, "longitude": 4.48, "country": "NL", "weather_vulnerability": 0.45},
        {"port_code": "USLAX", "port_name": "Los Angeles", "latitude": 33.74, "longitude": -118.27, "country": "US", "weather_vulnerability": 0.25},
        {"port_code": "HKHKG", "port_name": "Hong Kong", "latitude": 22.29, "longitude": 114.16, "country": "HK", "weather_vulnerability": 0.70},
        {"port_code": "PHMNL", "port_name": "Manila", "latitude": 14.58, "longitude": 120.97, "country": "PH", "weather_vulnerability": 0.85},
        {"port_code": "INBOM", "port_name": "Mumbai", "latitude": 18.93, "longitude": 72.84, "country": "IN", "weather_vulnerability": 0.60},
        {"port_code": "AUSYD", "port_name": "Sydney", "latitude": -33.86, "longitude": 151.21, "country": "AU", "weather_vulnerability": 0.20},
        {"port_code": "SAJED", "port_name": "Jeddah", "latitude": 21.49, "longitude": 39.19, "country": "SA", "weather_vulnerability": 0.15},
        {"port_code": "USHOU", "port_name": "Houston", "latitude": 29.75, "longitude": -95.29, "country": "US", "weather_vulnerability": 0.55},
        {"port_code": "ZADUR", "port_name": "Durban", "latitude": -29.87, "longitude": 31.05, "country": "ZA", "weather_vulnerability": 0.35},
        {"port_code": "ARBUE", "port_name": "Buenos Aires", "latitude": -34.61, "longitude": -58.37, "country": "AR", "weather_vulnerability": 0.20},
        {"port_code": "CNSZX", "port_name": "Shenzhen", "latitude": 22.54, "longitude": 113.93, "country": "CN", "weather_vulnerability": 0.65},
    ]
    insert("ports", ports)
    print(f"  ✓ ports ({len(ports)} rows)")


def seed_historical_disruptions():
    now = datetime.utcnow()
    disruptions = [
        {
            "disruption_id": str(uuid4()),
            "event_name": "Typhoon Haiyan 2013",
            "event_type": "typhoon",
            "region": "South China Sea",
            "avg_delay_days": 8.0,
            "estimated_cost_usd": 2_800_000_000,
            "ports_affected": ["PHMNL", "HKHKG", "CNSHA"],
            "lessons": "Category 5 typhoons in this corridor require pre-emptive rerouting 72+ hours before landfall. Manila port closed for 5 days. Vessels diverted to Singapore added 4 days transit.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Hurricane Harvey 2017",
            "event_type": "hurricane",
            "region": "Gulf of Mexico",
            "avg_delay_days": 10.0,
            "estimated_cost_usd": 8_000_000_000,
            "ports_affected": ["USHOU", "USLAX"],
            "lessons": "Gulf ports shut for 6+ days. Houston port closures caused 14-day backlog. Cargo diverted to Los Angeles/Long Beach overwhelmed West Coast ports.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Cyclone Idai 2019",
            "event_type": "cyclone",
            "region": "Indian Ocean",
            "avg_delay_days": 6.0,
            "estimated_cost_usd": 1_500_000_000,
            "ports_affected": ["ZADUR", "INBOM"],
            "lessons": "Category 3+ cyclones in Mozambique Channel disrupt Durban-bound traffic. Mumbai as alternate port absorbs some capacity but adds 5-7 days.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Winter Storm Uri 2021",
            "event_type": "winter_storm",
            "region": "North Atlantic",
            "avg_delay_days": 5.0,
            "estimated_cost_usd": 3_200_000_000,
            "ports_affected": ["NLRTM", "USLAX"],
            "lessons": "Severe winter storms in North Atlantic delay Rotterdam-bound vessels by 4-8 days. Recommended route adjustment: southern crossing via Azores when lead time >48h.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Typhoon Mangkhut 2018",
            "event_type": "typhoon",
            "region": "South China Sea",
            "avg_delay_days": 7.0,
            "estimated_cost_usd": 2_100_000_000,
            "ports_affected": ["HKHKG", "CNSZX", "PHMNL"],
            "lessons": "Super typhoon closed Hong Kong and Shenzhen ports for 4 days. Cargo rerouted through Shanghai added 6 days. Insurance claims exceeded $500M.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Monsoon Flooding 2019",
            "event_type": "flood",
            "region": "Indian Ocean",
            "avg_delay_days": 3.0,
            "estimated_cost_usd": 900_000_000,
            "ports_affected": ["INBOM", "SGSIN"],
            "lessons": "Monsoon season (Jun-Sep) closes Mumbai port operations ~15% of days. Average delay 2-3 days per incident. Pre-stocking at Singapore reduces downstream impact.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Hurricane Dorian 2019",
            "event_type": "hurricane",
            "region": "Gulf of Mexico",
            "avg_delay_days": 7.0,
            "estimated_cost_usd": 3_400_000_000,
            "ports_affected": ["USHOU", "USLAX"],
            "lessons": "Category 5 hurricane disrupted Gulf shipping lanes for 8 days. Houston cargo backlog took 3 weeks to clear. Early rerouting to LA saved an estimated $800M.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Suez Canal Blockage 2021",
            "event_type": "obstruction",
            "region": "Red Sea",
            "avg_delay_days": 12.0,
            "estimated_cost_usd": 9_600_000_000,
            "ports_affected": ["NLRTM", "SAJED", "SGSIN"],
            "lessons": "6-day blockage caused 12-day average delays for all Suez-dependent routes. Rerouting via Cape of Good Hope adds 9 days and $300K fuel cost per vessel.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Typhoon Goni 2020",
            "event_type": "typhoon",
            "region": "South China Sea",
            "avg_delay_days": 5.0,
            "estimated_cost_usd": 1_200_000_000,
            "ports_affected": ["PHMNL", "CNSHA"],
            "lessons": "Category 4 typhoon hit Manila directly. Port operations suspended for 4 days. Ships already in transit diverted to Hong Kong. Advance warning enabled 60% of cargo to be rerouted pre-impact.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Atlantic Storm Dennis 2020",
            "event_type": "winter_storm",
            "region": "North Atlantic",
            "avg_delay_days": 4.0,
            "estimated_cost_usd": 1_800_000_000,
            "ports_affected": ["NLRTM", "ARBUE"],
            "lessons": "Severe North Atlantic conditions forced Rotterdam-bound vessels to hold at UK ports for 3-5 days. Southern route via Azores proved viable with 2-day added transit.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Tropical Storm Mara 2024",
            "event_type": "storm",
            "region": "South China Sea",
            "avg_delay_days": 4.0,
            "estimated_cost_usd": 800_000_000,
            "ports_affected": ["PHMNL", "HKHKG", "CNSZX"],
            "lessons": "Category 2 storm near Manila disrupted trans-Pacific routes. 4-day average delay. Rerouting via Malacca Strait reduced impact for ships with >48h lead time. Real-time monitoring caught this 36h before major news outlets.",
        },
        {
            "disruption_id": str(uuid4()),
            "event_name": "Pacific Typhoon Season 2023",
            "event_type": "typhoon",
            "region": "South China Sea",
            "avg_delay_days": 5.5,
            "estimated_cost_usd": 3_500_000_000,
            "ports_affected": ["CNSHA", "HKHKG", "CNSZX", "PHMNL"],
            "lessons": "Above-average typhoon season with 17 named storms. Cumulative impact: 5.5-day average delays across all trans-Pacific routes. Pre-season route planning and real-time monitoring reduced losses by estimated 30% compared to 2018.",
        },
    ]
    insert("historical_disruptions", disruptions)
    print(f"  ✓ historical_disruptions ({len(disruptions)} rows)")


def seed_all():
    print("Seeding data...")
    seed_shipping_routes()
    seed_ports()
    seed_historical_disruptions()
    print("Seeding complete.")
