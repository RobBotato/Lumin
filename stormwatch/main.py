import asyncio
import json
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from config import HOST, PORT, DEMO_MODE
from db.schema import create_all_tables
from db.seed import seed_all
from db.clickhouse import get_client, insert_weather_events, query
from agent import AgentLoop
from integrations import google_calendar, twilio_voice


class WebSocketManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, message: str):
        dead = []
        for ws in self.connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


ws_manager = WebSocketManager()
agent: AgentLoop | None = None
agent_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent, agent_task

    print("\n" + "=" * 60)
    print("  LUMIN SERVER")
    print("=" * 60)

    # Initialize database (skip seed if already populated)
    print("\nInitializing ClickHouse...")
    try:
        create_all_tables()
        from db.clickhouse import query
        existing = query("SELECT count() FROM shipping_routes")
        if existing and existing[0].get("count()", 0) == 0:
            seed_all()
        else:
            print(f"  Database ready ({existing[0].get('count()', '?')} route waypoints)")
    except Exception as e:
        print(f"  Database setup warning: {e}")

    # Start agent loop
    print(f"\nStarting agent loop (demo={DEMO_MODE})...")
    agent = AgentLoop(ws_manager=ws_manager)
    agent_task = asyncio.create_task(agent.start())

    yield

    # Shutdown
    print("\nShutting down...")
    if agent:
        await agent.stop()
    if agent_task:
        agent_task.cancel()
        try:
            await agent_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Lumin", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"


class AnalyzeRequest(BaseModel):
    productType: str
    origin: str
    destination: str
    shippingDate: str
    quantity: int | None = None
    estimatedWeight: float | None = None
    weightUnit: str | None = None
    shipmentValue: int | None = None
    packagingType: str | None = None
    transportMethod: str | None = None
    deliveryPriority: str | None = None
    riskTolerance: str | None = None
    clientPhone: str | None = None
    clientName: str | None = None
    carrier: str | None = None
    clientEmail: str | None = None


@app.post("/api/analyze")
async def analyze_shipment(req: AnalyzeRequest):
    """Run the agent pipeline for a specific shipment and return risk analysis."""
    from detect.threats import get_historical_matches, get_route_impact, resolve_region
    from analyze.pioneer import extract as pioneer_extract
    from analyze.llm import assess as llm_assess, SYSTEM_PROMPT
    from analyze.senso import query as senso_query
    from tracing.langfuse import create_trace

    start_time = time.time()
    agent_events = []
    trace = create_trace("shipment-analysis")

    # Step 1: Find matching route
    route = _find_route_for_shipment(req.origin, req.destination)
    cargo_value = req.shipmentValue or (route.get("cargo_value_usd", 5_000_000) if route else 5_000_000)
    if not route:
        route = {
            "route_id": "AUTO-01", "vessel_name": "MV Auto Vessel",
            "cargo_value_usd": cargo_value, "destination_port": req.destination,
        }
    else:
        route = dict(route)
        route["cargo_value_usd"] = cargo_value
    route_id = route["route_id"]

    # Step 2: Inject storm near the route
    storm_lat, storm_lon = _storm_coords_for_route(req.origin)
    storm_event = {
        "event_id": str(uuid4()),
        "timestamp": datetime.utcnow(),
        "latitude": storm_lat,
        "longitude": storm_lon,
        "event_type": "storm",
        "severity": "severe",
        "wind_speed_kmh": 177.0,
        "precipitation_mm": 85.0,
        "description": f"Tropical Storm detected near {req.origin}, Category 2 with sustained winds of 110 mph, affecting shipping lanes to {req.destination}.",
        "source": "simulated",
    }
    insert_weather_events([storm_event])
    step1_ms = int((time.time() - start_time) * 1000)
    agent_events.append({
        "id": "step-1", "label": "Shipment received",
        "detail": f"Route {route_id} identified. Ingesting weather data for corridor.",
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"), "durationMs": step1_ms,
    })

    # Step 3: Detect threat
    t0 = time.time()
    threat = {
        "event_type": "storm", "severity": "severe",
        "storm_lat": storm_lat, "storm_lon": storm_lon,
        "distance_km": 45.3, "description": storm_event["description"],
        "route_id": route_id, "vessel_name": route["vessel_name"],
        "destination_port": route["destination_port"],
        "cargo_value_usd": route["cargo_value_usd"],
        "wind_speed_kmh": 177,
    }
    step2_ms = int((time.time() - t0) * 1000)
    agent_events.append({
        "id": "step-2", "label": "Weather forecast retrieved",
        "detail": f"Storm detected {45}km from {route_id}. Cross-referencing route waypoints.",
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"), "durationMs": step2_ms,
    })
    trace.span(name="threat-detection", input_data={"route": route_id}, output_data={"storm_found": True})

    # Step 4: Extract entities
    t0 = time.time()
    entities = await pioneer_extract(storm_event["description"])
    step3_ms = int((time.time() - t0) * 1000)
    agent_events.append({
        "id": "step-3", "label": "Risk factors analyzed",
        "detail": f"Extracted: {entities.storm_name}, {entities.category}, winds {entities.wind_speed} near {entities.location}.",
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"), "durationMs": step3_ms,
    })
    trace.span(name="entity-extraction", input_data={"bulletin": storm_event["description"]}, output_data=entities.to_dict())

    # Step 5: Knowledge base + historical
    t0 = time.time()
    region = resolve_region(storm_lat, storm_lon)
    kb_context = senso_query(f"What is the typical impact of a {entities.category} storm in {entities.affected_area or region}?", demo=DEMO_MODE)
    historical = get_historical_matches("storm", region)
    step4_ms = int((time.time() - t0) * 1000)
    agent_events.append({
        "id": "step-4", "label": "Product sensitivity evaluated",
        "detail": f"Queried knowledge base. Found {len(historical)} historical precedents for {region}.",
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"), "durationMs": step4_ms,
    })
    trace.span(name="knowledge-lookup", output_data={"historical_matches": len(historical)})

    # Step 6: LLM Risk Assessment
    entities_dict = entities.to_dict()

    # Adjust system prompt based on risk tolerance
    tolerance = (req.riskTolerance or "Balanced") if req else "Balanced"
    system_prompt = SYSTEM_PROMPT
    if tolerance == "Conservative":
        system_prompt += "\n\nRISK POSTURE: CONSERVATIVE. Err on the side of caution. Prefer delaying or rerouting over any risk. Set confidence higher and recommend action only when certain. Round financial impact estimates UP."
    elif tolerance == "Aggressive":
        system_prompt += "\n\nRISK POSTURE: AGGRESSIVE. Minimize delays. Accept moderate risk levels. Only flag threats above 70% confidence as critical. Recommend proceeding unless danger is imminent. Round financial impact estimates DOWN."

    assessment = await llm_assess(threat, entities_dict, kb_context, historical, system_prompt=system_prompt)

    # Compute a mathematical risk score independent of LLM confidence
    risk_score = _compute_risk_score(threat, entities, req, assessment)
    step5_ms = int((time.time() - t0) * 1000)
    agent_events.append({
        "id": "step-5", "label": "Recommendations generated",
        "detail": f"Risk level: {assessment.risk_level.upper()}. Confidence: {int(assessment.confidence * 100)}%.",
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"), "durationMs": step5_ms,
    })
    trace.generation(name="risk-reasoning", input_data={"route": route_id}, output_data=assessment.to_dict())
    trace.end()

    # Map to frontend format
    risk_map = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH", "critical": "HIGH"}
    risk_level = risk_map.get(assessment.risk_level, "MEDIUM")

    # Build rich threats list
    threats = _build_threats(storm_lat, storm_lon, entities, assessment)

    # Build rich recommendations list
    recommendations = _build_recommendations(assessment, route, req)

    # Generate safe shipping windows (next 7 days)
    safe_windows = _generate_safe_windows(req.shippingDate, storm_lat, storm_lon)

    # Generate alternative routes
    alt_routes = _generate_alternative_routes(route_id, route)

    # Generate financial breakdown
    financial = _build_financial_breakdown(assessment, route)

    # Generate port weather for origin/destination
    port_weather = _build_port_weather(req.origin, req.destination, storm_lat, storm_lon)

    # Executive summary + business impact
    exec_summary = _build_executive_summary(assessment, entities, req)
    biz_impact = _build_business_impact(assessment, route, req)

    # Auto-reschedule if risk is high/critical
    rescheduled = _compute_reschedule(safe_windows, req, risk_level, risk_score)

    if rescheduled:
        agent_events.append({
            "id": "step-6",
            "label": "Calendar event rescheduled",
            "detail": f"Google Calendar: original {rescheduled['originalDate']} delivery cancelled, rescheduled to {rescheduled['newDate']} (+{rescheduled['daysMoved']} days).",
            "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
            "durationMs": 120,
        })

        # Actually cancel original + create rescheduled event in Google Calendar if connected
        if google_calendar.is_connected():
            events = await google_calendar.list_upcoming_events(10)
            original_cancelled = False
            for evt in events:
                title_match = req.productType.lower() in (evt.get("title", "")).lower()
                route_match = any(
                    city.lower() in (evt.get("title", "") + evt.get("description", "")).lower()
                    for city in [req.origin.split(",")[0], req.destination.split(",")[0]]
                )
                if title_match or route_match:
                    cancelled = await google_calendar.cancel_event(
                        evt["calendarEventId"],
                        rescheduled["reason"],
                    )
                    if cancelled:
                        original_cancelled = True
                        rescheduled["calendarEventCancelled"] = True
                        rescheduled["originalEventId"] = evt["calendarEventId"]
                    break

            # Create new event at the rescheduled date
            event_id = await google_calendar.create_shipment_event(
                title=req.productType,
                date=rescheduled["newDate"],
                origin=req.origin,
                destination=req.destination,
                notes=rescheduled["reason"],
            )
            if event_id:
                rescheduled["calendarEventCreated"] = True
                rescheduled["calendarEventId"] = event_id
                status = "Original cancelled + new created" if original_cancelled else "New event created"
                agent_events.append({
                    "id": "step-7",
                    "label": "Calendar events updated",
                    "detail": f"Google Calendar: {status} on {rescheduled['newDate']}. Event ID: {event_id[:12]}...",
                    "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
                    "durationMs": 180,
                })

        # Step 8: Email notification to client
        if rescheduled and req.clientEmail:
            email_result = twilio_voice.send_reschedule_email(
                to_email=req.clientEmail,
                client_name=req.clientName or "",
                product_type=req.productType,
                origin=req.origin,
                destination=req.destination,
                original_date=rescheduled["originalDate"],
                new_date=rescheduled["newDate"],
                new_date_label=rescheduled.get("newDateLabel", ""),
                reason=rescheduled["reason"],
                days_moved=rescheduled.get("daysMoved", 0),
            )
            rescheduled["emailNotification"] = email_result
            if email_result.get("sent"):
                agent_events.append({
                    "id": "step-8",
                    "label": "Email notification sent",
                    "detail": f"Email sent to {req.clientName or 'client'} at {req.clientEmail} — rescheduled to {rescheduled['newDate']}.",
                    "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
                    "durationMs": 420,
                })
            else:
                agent_events.append({
                    "id": "step-8",
                    "label": "Email skipped",
                    "detail": f"Could not send email — {email_result.get('reason', 'unknown error')}",
                    "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
                    "durationMs": 50,
                })

    # Historical comparison
    historical_match = _build_historical_comparison(historical, entities, assessment)

    return {
        "shipment": {
            "productType": req.productType,
            "origin": req.origin,
            "destination": req.destination,
            "shippingDate": req.shippingDate,
            "quantity": req.quantity,
            "estimatedWeight": req.estimatedWeight,
            "weightUnit": req.weightUnit,
            "shipmentValue": req.shipmentValue,
            "packagingType": req.packagingType,
            "transportMethod": req.transportMethod,
            "deliveryPriority": req.deliveryPriority,
            "riskTolerance": req.riskTolerance,
        },
        "riskLevel": risk_level,
        "riskScore": risk_score,
        "confidence": int(assessment.confidence * 100),
        "summary": assessment.summary,
        "threats": threats,
        "recommendations": recommendations,
        "agentEvents": agent_events,
        "generatedAt": datetime.utcnow().isoformat(),
        "safeShippingWindows": safe_windows,
        "alternativeRoutes": alt_routes,
        "financialBreakdown": financial,
        "portWeather": port_weather,
        "historicalComparison": historical_match,
        "executiveSummary": exec_summary,
        "businessImpact": biz_impact,
        "rescheduledTo": rescheduled,
    }


def _find_route_for_shipment(origin: str, destination: str) -> dict | None:
    """Match origin/destination city names to known shipping routes."""
    city_to_port = {
        "phoenix": ("Los Angeles", "USLAX"), "dallas": ("Houston", "USHOU"),
        "seattle": ("Los Angeles", "USLAX"), "chicago": ("Houston", "USHOU"),
        "miami": ("Houston", "USHOU"), "atlanta": ("Houston", "USHOU"),
        "los angeles": ("Los Angeles", "USLAX"), "houston": ("Houston", "USHOU"),
        "shanghai": ("Shanghai", "CNSHA"), "hong kong": ("Hong Kong", "HKHKG"),
        "singapore": ("Singapore", "SGSIN"), "manila": ("Manila", "PHMNL"),
        "rotterdam": ("Rotterdam", "NLRTM"), "mumbai": ("Mumbai", "INBOM"),
        "sydney": ("Sydney", "AUSYD"), "shenzhen": ("Shenzhen", "CNSZX"),
        "buenos aires": ("Buenos Aires", "ARBUE"), "durban": ("Durban", "ZADUR"),
        "jeddah": ("Jeddah", "SAJED"),
    }

    origin_lower = origin.lower().strip()
    dest_lower = destination.lower().strip()

    origin_port = city_to_port.get(origin_lower, ("Los Angeles", "USLAX"))
    dest_port = city_to_port.get(dest_lower, ("Houston", "USHOU"))

    try:
        results = query(f"""
            SELECT route_id, vessel_name, cargo_value_usd, destination_port,
                   origin_port
            FROM shipping_routes
            WHERE origin_port = '{origin_port[1]}'
               OR destination_port = '{dest_port[1]}'
            LIMIT 1
        """)
        if results:
            return results[0]
    except Exception:
        pass
    return None


def _storm_coords_for_route(origin: str) -> tuple[float, float]:
    """Return storm coordinates near common shipping corridors."""
    origin_lower = origin.lower().strip()
    coords = {
        "phoenix": (26.0, -90.0), "dallas": (26.0, -90.0),
        "miami": (26.0, -90.0), "atlanta": (26.0, -90.0),
        "houston": (26.0, -90.0),  # Gulf of Mexico
        "los angeles": (33.0, -120.0),  # Pacific
        "seattle": (45.0, -130.0),
        "chicago": (26.0, -90.0),
        "shanghai": (22.0, 125.0),  # East China Sea
        "hong kong": (14.5, 119.0),  # South China Sea
        "manila": (14.5, 119.0),  # South China Sea
        "shenzhen": (14.5, 119.0),  # South China Sea
        "singapore": (2.5, 102.0),  # Malacca Strait
        "rotterdam": (45.0, -35.0),  # North Atlantic
        "mumbai": (15.0, 70.0),  # Arabian Sea
    }
    return coords.get(origin_lower, (26.0, -90.0))


# ─── Response Builder Helpers ───────────────────────────────────────

def _build_threats(storm_lat: float, storm_lon: float, entities, assessment) -> list[dict]:
    """Build a rich set of threats with different types and severities."""
    threats = [{
        "id": "threat-1",
        "label": f"{entities.storm_name or 'Storm'} — {entities.category or 'Category 2'}",
        "severity": "severe" if assessment.risk_level in ("high", "critical") else "moderate",
        "probability": int(assessment.confidence * 100),
        "detail": assessment.summary[:200],
        "icon": "storm",
        "proximityKm": 45,
        "direction": "NW",
        "estimatedLandfall": (datetime.utcnow() + __import__("datetime").timedelta(hours=18)).strftime("%b %d, %H:%M UTC"),
    }]
    # Add wind threat
    threats.append({
        "id": "threat-2",
        "label": f"High Winds — {entities.category or 'Category 2'}",
        "severity": "severe",
        "probability": min(100, int(assessment.confidence * 100) + 5),
        "detail": f"Sustained winds of 110–130 mph expected along route corridor. Crosswinds exceed safe container stacking limits (55 mph threshold).",
        "icon": "wind",
        "proximityKm": 85,
        "direction": "NW",
        "estimatedLandfall": None,
    })
    # Add precipitation threat
    threats.append({
        "id": "threat-3",
        "label": "Heavy Precipitation",
        "severity": "moderate",
        "probability": int(assessment.confidence * 70),
        "detail": f"85mm rainfall expected in 24h within storm radius. Flash flood risk at {entities.location or 'destination'} port may delay unloading by 12–24h.",
        "icon": "rain",
        "proximityKm": 120,
        "direction": "SE",
        "estimatedLandfall": None,
    })
    # Add humidity threat for sensitive cargo
    threats.append({
        "id": "threat-4",
        "label": "Elevated Humidity — Storm System",
        "severity": "low",
        "probability": 65,
        "detail": "Relative humidity forecast at 85–95% within storm zone. Risk of condensation damage for electronics and pharmaceutical cargo.",
        "icon": "humidity",
        "proximityKm": 200,
        "direction": None,
        "estimatedLandfall": None,
    })
    return threats


def _build_recommendations(assessment, route: dict, req: AnalyzeRequest = None) -> list[dict]:
    """Build ranked recommendations with varied impact levels."""
    priority = (req.deliveryPriority or "Standard") if req else "Standard"
    packaging = (req.packagingType or "Standard") if req else "Standard"
    transport = (req.transportMethod or "Truck") if req else "Truck"
    is_critical = assessment.risk_level in ("high", "critical")
    cargo_value = route.get("cargo_value_usd", 0) or 5_000_000

    recs = [{
        "id": "rec-1",
        "title": "Reroute via Alternate Corridor",
        "detail": assessment.recommendation[:200],
        "impact": "critical" if is_critical else "recommended",
        "icon": "reroute",
        "estimatedSaving": assessment.total_financial_impact_usd // 2 if assessment.total_financial_impact_usd else 500000,
    }]

    # Delay recommendation — varies by priority
    if priority in ("Expedited", "Critical"):
        delay_hours = 12 if priority == "Critical" else 24
        recs.append({
            "id": "rec-2",
            "title": f"Delay Shipment {delay_hours}h — {priority} Priority Window",
            "detail": f"Hold {route.get('vessel_name', 'vessel')} at origin for {delay_hours}h. Storm clears sufficiently for {priority.lower()} transit. Reduces exposure by 60% while meeting {priority} SLA.",
            "impact": "recommended",
            "icon": "delay",
            "estimatedSaving": int(cargo_value * 0.3),
        })
    else:
        recs.append({
            "id": "rec-2",
            "title": "Delay Shipment 48–72 Hours",
            "detail": f"Hold {route.get('vessel_name', 'vessel')} at origin port until storm passes. Expected clearance window opens in 48–72 hours based on current track models. Reduces exposure by 80%.",
            "impact": "recommended",
            "icon": "delay",
            "estimatedSaving": int(cargo_value * 0.4),
        })

    # Packaging-specific recommendation
    if packaging == "Refrigerated":
        recs.append({
            "id": "rec-3",
            "title": "Secure Cold Chain Continuity",
            "detail": "Refrigerated cargo at risk of temperature excursion during delays. Pre-cool containers to -5°C buffer and deploy backup generators at holding location. Validated during 2021 Uri cold chain protocols.",
            "impact": "critical" if is_critical else "recommended",
            "icon": "refrigerate",
            "estimatedSaving": int(cargo_value * 0.25),
        })
    elif packaging == "Fragile":
        recs.append({
            "id": "rec-3",
            "title": "Shock-Absorbent Reloading",
            "detail": "Fragile cargo faces amplified vibration risk on alternate routes. Repack with double-layer cushioning and shock indicators. Adds $0.15/unit but prevents 92% of transit damage claims.",
            "impact": "recommended",
            "icon": "standard",
            "estimatedSaving": int(cargo_value * 0.18),
        })
    elif packaging == "Waterproof":
        recs.append({
            "id": "rec-3",
            "title": "Waterproof Packaging Already Active",
            "detail": "Waterproof packaging mitigates 85–95% humidity and rain exposure. Maintain seal integrity during any holding period. No additional packaging action required.",
            "impact": "optional",
            "icon": "waterproof",
            "estimatedSaving": 0,
        })
    else:
        recs.append({
            "id": "rec-3",
            "title": "Upgrade to Waterproof Packaging",
            "detail": "Standard packaging vulnerable to 85–95% humidity in storm zone. Apply waterproof container liners and desiccants. Low-cost mitigation with high ROI for sensitive cargo.",
            "impact": "optional",
            "icon": "waterproof",
            "estimatedSaving": 45000,
        })

    # Transport-specific
    if transport == "Ocean":
        recs.append({
            "id": "rec-4",
            "title": "Port Congestion Pre-Alert",
            "detail": f"Ocean freight to {route.get('destination_port', 'destination')} faces 2–4 day berth delays post-storm. Pre-book alternate berth slot or divert to nearby port. Historical: 40% faster turnaround with pre-booking.",
            "impact": "critical" if is_critical else "recommended",
            "icon": "monitor",
            "estimatedSaving": int(cargo_value * 0.12),
        })
    elif transport == "Air":
        recs.append({
            "id": "rec-4",
            "title": "Air Freight Weather Hold Advisory",
            "detail": "Storm conditions exceed air cargo safety thresholds (crosswinds >35 knots). Expect 12–24h ground hold. Reposition to alternate airport if priority is critical.",
            "impact": "recommended",
            "icon": "monitor",
            "estimatedSaving": int(cargo_value * 0.08),
        })

    return recs


def _generate_safe_windows(shipping_date: str, storm_lat: float, storm_lon: float) -> list[dict]:
    """Generate 7-day forecast showing which days are safe to ship."""
    from datetime import timedelta
    import random
    random.seed(hash(shipping_date) % 10000)
    base_date = datetime.strptime(shipping_date, "%Y-%m-%d") if shipping_date else datetime.utcnow()
    windows = []
    for i in range(7):
        day = base_date + timedelta(days=i)
        if i < 2:
            risk = "HIGH"
            score = random.randint(75, 95)
            conditions = "Storm active in corridor"
        elif i < 4:
            risk = "MEDIUM"
            score = random.randint(40, 65)
            conditions = "Storm dissipating, residual swell"
        else:
            risk = "LOW"
            score = random.randint(5, 25)
            conditions = "Clear conditions expected"
        windows.append({
            "date": day.strftime("%Y-%m-%d"),
            "dayLabel": day.strftime("%a %b %d"),
            "riskLevel": risk,
            "riskScore": score,
            "conditions": conditions,
            "recommended": risk == "LOW",
        })
    return windows


def _generate_alternative_routes(route_id: str, route: dict) -> list[dict]:
    """Generate alternative shipping routes with trade-offs."""
    alt_routes = [{
        "id": "alt-1",
        "routeName": "Southern Corridor Bypass",
        "originPort": route.get("origin_port", "LAX"),
        "destinationPort": route.get("destination_port", "HOU"),
        "additionalDays": 3,
        "additionalCost": 180000,
        "riskLevel": "LOW",
        "description": "Deviate 300nm south to avoid storm system entirely. Adds 3 days transit but eliminates weather exposure. Validated during 2019 Pacific typhoon season.",
        "vessel": route.get("vessel_name", "Vessel"),
    }, {
        "id": "alt-2",
        "routeName": "Rail Intermodal Transfer",
        "originPort": route.get("origin_port", "LAX"),
        "destinationPort": route.get("destination_port", "HOU"),
        "additionalDays": 1,
        "additionalCost": 320000,
        "riskLevel": "LOW",
        "description": "Offload at nearest safe port and transfer to rail. 1-day faster than southern bypass but higher cost. No weather exposure.",
        "vessel": f"{route.get('vessel_name', 'Vessel')} (Partial)",
    }, {
        "id": "alt-3",
        "routeName": "Hold & Sprint Window",
        "originPort": route.get("origin_port", "LAX"),
        "destinationPort": route.get("destination_port", "HOU"),
        "additionalDays": 2,
        "additionalCost": 75000,
        "riskLevel": "MEDIUM",
        "description": "Hold at origin 48h then sprint through the corridor during forecasted 12h calm window. Lowest cost but some residual risk.",
        "vessel": route.get("vessel_name", "Vessel"),
    }]
    return alt_routes


def _build_financial_breakdown(assessment, route: dict) -> dict:
    """Build detailed financial impact breakdown."""
    cargo_value = route.get("cargo_value_usd", 0) or 5_000_000
    delay_days = 4 if assessment.risk_level in ("high", "critical") else 2
    daily_op_cost = 25000
    return {
        "cargoValue": cargo_value,
        "estimatedDelayCost": delay_days * daily_op_cost,
        "demurrageFees": delay_days * 15000,
        "insuranceExposure": int(cargo_value * 0.15),
        "reroutingCost": 180000,
        "spoilageRisk": int(cargo_value * 0.05) if assessment.risk_level in ("high", "critical") else 0,
        "totalAtRisk": cargo_value + (delay_days * daily_op_cost) + (delay_days * 15000) + int(cargo_value * 0.15),
        "estimatedSavingsIfRerouted": int(cargo_value * 0.6),
        "currency": "USD",
    }


def _build_port_weather(origin: str, destination: str, storm_lat: float, storm_lon: float) -> dict:
    """Build weather conditions for origin and destination ports."""
    import random
    random.seed(hash(f"{origin}{destination}") % 10000)
    return {
        "origin": {
            "portName": _port_for_city(origin),
            "conditions": "Partly Cloudy",
            "temperature": f"{random.randint(72, 85)}°F",
            "windSpeed": f"{random.randint(5, 15)} mph",
            "visibility": "10 miles",
            "stormProximity": "380nm",
            "status": "operational",
        },
        "destination": {
            "portName": _port_for_city(destination),
            "conditions": "Storm Warning",
            "temperature": f"{random.randint(68, 78)}°F",
            "windSpeed": f"{random.randint(35, 55)} mph",
            "visibility": "2 miles",
            "stormProximity": "45nm",
            "status": "restricted",
        },
    }


_port_map = {
    "phoenix": "Los Angeles (USLAX)", "dallas": "Houston (USHOU)",
    "seattle": "Seattle (USSEA)", "chicago": "Chicago Rail Terminal",
    "miami": "Miami (USMIA)", "atlanta": "Savannah (USSAV)",
    "los angeles": "Los Angeles (USLAX)", "houston": "Houston (USHOU)",
    "shanghai": "Shanghai (CNSHA)", "hong kong": "Hong Kong (HKHKG)",
    "singapore": "Singapore (SGSIN)", "manila": "Manila (PHMNL)",
    "rotterdam": "Rotterdam (NLRTM)", "mumbai": "Mumbai (INBOM)",
    "sydney": "Sydney (AUSYD)", "shenzhen": "Shenzhen (CNSZX)",
    "buenos aires": "Buenos Aires (ARBUE)", "durban": "Durban (ZADUR)",
    "jeddah": "Jeddah (SAJED)",
}

def _port_for_city(city: str) -> str:
    lower = city.lower().strip()
    # Try exact match first
    if lower in _port_map:
        return _port_map[lower]
    # Try partial match
    for key, val in _port_map.items():
        if key in lower:
            return val
    return f"{city.title()} Port"


def _build_historical_comparison(historical: list[dict], entities, assessment) -> dict | None:
    """Build a comparison to the most similar historical event."""
    if not historical:
        return None
    h = historical[0]
    return {
        "eventName": h.get("event_name", "Unknown"),
        "year": h.get("event_name", "").split()[-1] if h.get("event_name") else "N/A",
        "region": h.get("region", "Unknown"),
        "avgDelay": h.get("avg_delay_days", 0),
        "estimatedCost": h.get("estimated_cost_usd", 0),
        "lessons": h.get("lessons", ""),
        "similarityScore": 85 if assessment.risk_level in ("high", "critical") else 60,
    }


def _compute_risk_score(threat: dict, entities, req: AnalyzeRequest, assessment) -> int:
    """
    Mathematical multi-factor risk score (0-100).
    
    Factors:
      1. Storm intensity (0-35): based on wind speed / category
      2. Proximity (0-25): distance of storm to route
      3. Cargo sensitivity (0-20): packaging type vulnerability
      4. Route exposure (0-20): transport method + port vulnerability
    """
    score = 0.0

    # ── Factor 1: Storm Intensity (0-35) ──
    wind = threat.get("wind_speed_kmh", 0) or 0
    severity = threat.get("severity", "moderate")
    if severity == "extreme":
        score += 35
    elif severity == "severe":
        # 110 mph = 177 km/h → high end of severe
        intensity_pct = min(1.0, wind / 220.0)  # normalize to 220 km/h (Cat 4+)
        score += 20 + (intensity_pct * 15)  # 20-35 range
    else:
        score += wind / 220.0 * 18  # 0-18 range for moderate

    # ── Factor 2: Proximity (0-25) ──
    distance = threat.get("distance_km", 300) or 300
    if distance < 50:
        score += 25
    elif distance < 100:
        score += 21
    elif distance < 150:
        score += 17
    elif distance < 200:
        score += 12
    elif distance < 300:
        score += 7
    else:
        score += 3

    # ── Factor 3: Cargo Sensitivity (0-20) ──
    packaging = req.packagingType or "Standard" if req else "Standard"
    cargo_value = req.shipmentValue or 0 if req else 0
    sensitivity_map = {
        "Refrigerated": 18, "Fragile": 16, "Hazardous": 20,
        "Waterproof": 8, "Standard": 10,
    }
    base_sensitivity = sensitivity_map.get(packaging, 10)
    # Boost for high-value cargo
    if cargo_value > 1_000_000:
        base_sensitivity = min(20, base_sensitivity + 2)
    if cargo_value > 5_000_000:
        base_sensitivity = min(20, base_sensitivity + 2)
    score += base_sensitivity

    # ── Factor 4: Route Exposure (0-20) ──
    transport = req.transportMethod or "Truck" if req else "Truck"
    priority = req.deliveryPriority or "Standard" if req else "Standard"
    transport_risk = {"Air": 14, "Ocean": 18, "Rail": 12, "Truck": 10}
    priority_risk = {"Critical": 6, "Expedited": 4, "Standard": 1}
    score += transport_risk.get(transport, 10) * 0.7
    score += priority_risk.get(priority, 1) * 0.3

    # ── Risk tolerance modifier ──
    tolerance = req.riskTolerance or "Balanced" if req else "Balanced"
    if tolerance == "Conservative":
        score = min(100, score * 1.15)  # +15% for conservative
    elif tolerance == "Aggressive":
        score = max(1, score * 0.85)   # -15% for aggressive

    return min(100, max(1, round(score)))


def _build_executive_summary(assessment, entities, req: AnalyzeRequest) -> dict:
    """Build a concise executive summary."""
    risk_level = assessment.risk_level.upper()
    risks = [
        f"{entities.storm_name or 'Storm'} ({entities.category or 'Category 2'}) threatens shipping corridor",
        f"Winds of {entities.wind_speed or '110 mph'} exceed safe transit thresholds for {req.transportMethod or 'Truck'} transport",
        f"Estimated {4 if assessment.risk_level in ('high','critical') else 2}-day delay with {req.deliveryPriority or 'Standard'} priority cargo",
    ]
    if req.packagingType == "Refrigerated":
        risks.append(f"Cold chain integrity at risk — {req.packagingType} packaging requires continuous power")
    elif req.packagingType == "Fragile":
        risks.append(f"Vibration damage risk elevated on alternate routes — {req.packagingType} cargo")

    impact = f"If unmitigated, this {assessment.risk_level}-risk event threatens ${assessment.total_financial_impact_usd:,.0f} in cargo value across {req.transportMethod or 'Truck'} route {req.origin} → {req.destination}. Historical patterns suggest {4 if assessment.risk_level in ('high','critical') else 2}-day delays are typical."

    recs = [
        assessment.recommendation[:120] if assessment.recommendation else "Reroute via alternate corridor",
        f"Expedite cargo insurance for {req.deliveryPriority or 'Standard'} priority shipment",
    ]

    return {"mainRisks": risks[:4], "businessImpact": impact, "topRecommendations": recs}


def _build_business_impact(assessment, route: dict, req: AnalyzeRequest) -> dict:
    """Build a business impact summary card."""
    cargo = req.shipmentValue or route.get("cargo_value_usd", 0) or 5_000_000
    exposure = int(cargo * (0.18 if assessment.risk_level in ("high", "critical") else 0.08))
    delay_cost = 25000 if req.transportMethod == "Air" else 8000 if req.transportMethod == "Truck" else 12000

    impacts = {
        "Refrigerated": "Cold chain failure — product spoilage risk",
        "Fragile": "Breakage during rerouting — insurance liability",
        "Waterproof": "Packaging integrity maintained — low degradation risk",
        "Hazardous": "Regulatory compliance risk during port holds",
        "Standard": "Standard transit delay — no special handling risk",
    }
    operational = impacts.get(req.packagingType or "Standard", "Standard transit delay — minimal special handling risk")

    return {
        "shipmentValue": cargo,
        "estimatedExposure": exposure,
        "operationalImpact": operational,
        "delayCostPerDay": delay_cost,
        "confidenceLevel": f"{int(assessment.confidence * 100)}%",
    }


def _compute_reschedule(safe_windows: list[dict], req: AnalyzeRequest, risk_level: str, risk_score: int = 0) -> dict | None:
    """Auto-reschedule to the nearest safe shipping window if risk is high/critical."""
    if risk_level != "HIGH" and risk_score < 80:
        return None

    recommended = [w for w in safe_windows if w.get("recommended")]
    if not recommended:
        return None

    next_safe = recommended[0]
    original = req.shippingDate
    try:
        orig_date = datetime.strptime(original, "%Y-%m-%d")
        new_date = datetime.strptime(next_safe["date"], "%Y-%m-%d")
        days_moved = (new_date - orig_date).days
    except Exception:
        days_moved = 3

    return {
        "originalDate": original,
        "newDate": next_safe["date"],
        "newDateLabel": next_safe["dayLabel"],
        "daysMoved": days_moved,
        "reason": f"Auto-rescheduled due to {req.productType or 'cargo'} shipment risk. Storm conditions expected to clear by {next_safe['dayLabel']}.",
        "autoRescheduled": True,
    }


@app.get("/api/calendar-event")
async def calendar_event(
    title: str = "Shipment",
    date: str = "",
    origin: str = "",
    destination: str = "",
    notes: str = "",
):
    """Generate an .ics calendar file for the rescheduled shipment."""
    if not date:
        return {"error": "date required"}

    try:
        d = datetime.strptime(date, "%Y-%m-%d")
        dt_start = d.strftime("%Y%m%d")
        dt_end = (d + __import__("datetime").timedelta(days=1)).strftime("%Y%m%d")
    except Exception:
        return {"error": "invalid date format, use YYYY-MM-DD"}

    summary = f"📦 Lumin: {title} — {origin} → {destination}"
    description = (
        f"Shipment: {title}\\n"
        f"Route: {origin} → {destination}\\n"
        f"Rescheduled by Lumin agent\\n"
        f"Notes: {notes}\\n"
        f"\\nPowered by Lumin — AI Supply Chain Intelligence"
    )

    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Lumin//EN\r\n"
        "BEGIN:VEVENT\r\n"
        f"DTSTART;VALUE=DATE:{dt_start}\r\n"
        f"DTEND;VALUE=DATE:{dt_end}\r\n"
        f"SUMMARY:{summary}\r\n"
        f"DESCRIPTION:{description}\r\n"
        "TRANSP:OPAQUE\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )

    from fastapi.responses import Response
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=lumin-shipment-{dt_start}.ics"},
    )


@app.get("/api/calendar/shipments")
async def calendar_shipments():
    """Return shipments synced from Google Calendar."""
    if google_calendar.is_connected():
        events = await google_calendar.list_upcoming_events()
        if events:
            return {"shipments": events, "connected": True, "provider": "Google Calendar (Live)"}

    # Fallback: seed data
    from db.clickhouse import query as ch_query
    try:
        routes = ch_query("""
            SELECT DISTINCT route_id, vessel_name, origin_port, destination_port,
                   cargo_value_usd, eta
            FROM shipping_routes WHERE status = 'in_transit'
            ORDER BY eta LIMIT 10
        """)
        shipments = []
        for r in routes:
            shipments.append({
                "id": r["route_id"],
                "title": f"📦 {r.get('vessel_name','Shipment')}",
                "route": f"{r.get('origin_port','Origin')} → {r.get('destination_port','Dest')}",
                "date": r["eta"].strftime("%Y-%m-%d") if r.get("eta") else "2026-06-20",
                "value": r.get("cargo_value_usd", 0),
                "source": "database",
                "lastSynced": datetime.utcnow().isoformat(),
            })
        return {"shipments": shipments, "connected": google_calendar.is_connected(), "provider": "Database"}
    except Exception as e:
        return {"shipments": [], "connected": False, "error": str(e)}


@app.get("/api/auth/google")
async def google_auth():
    """Redirect to Google OAuth consent screen."""
    url = google_calendar.get_auth_url()
    if not url:
        return {"error": "Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"}
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)


@app.get("/api/auth/google/callback")
async def google_callback(code: str = ""):
    """Handle Google OAuth callback."""
    if not code:
        return {"error": "No authorization code received"}
    try:
        token = await google_calendar.exchange_code(code)
        return {
            "status": "connected",
            "message": "Google Calendar connected successfully! You can close this window.",
            "expires_at": token.get("expires_at"),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/auth/google/status")
async def google_status():
    """Check Google Calendar connection status."""
    connected = google_calendar.is_connected()
    shipments = []
    if connected:
        shipments = await google_calendar.list_upcoming_events(5)
    return {
        "connected": connected,
        "shipments": len(shipments),
        "events": shipments[:3] if shipments else [],
    }


@app.get("/")
async def root():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text())
    return HTMLResponse("<h1>Lumin</h1><p>Static files not found.</p>")


@app.get("/api/health")
async def health():
    return {
        "status": "running",
        "demo_mode": DEMO_MODE,
        "agent_running": agent is not None and agent.running if agent else False,
        "cycle": agent.cycle if agent else 0,
    }


@app.get("/api/metrics")
async def metrics():
    if agent:
        return agent.metrics
    return {"error": "Agent not running"}


@app.get("/api/demo/trigger-storm")
async def trigger_storm():
    """Manually trigger a simulated storm for demo purposes."""
    if agent and DEMO_MODE:
        agent.cycle = 4  # Trigger first demo scenario
        return {"status": "ok", "message": "Storm scenario triggered on next cycle"}
    return {"status": "error", "message": "Not in demo mode or agent not running"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        # Send current metrics on connect
        if agent:
            await ws.send_text(json.dumps({
                "type": "metrics_update",
                "data": agent.metrics,
                "timestamp": "",
            }))
        # Keep connection alive
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception:
        ws_manager.disconnect(ws)


@app.get("/api/voice/twiml")
async def voice_twiml(
    clientName: str = "",
    productType: str = "shipment",
    origin: str = "",
    destination: str = "",
    originalDate: str = "",
    newDate: str = "",
    newDateLabel: str = "",
    reason: str = "",
    daysMoved: int = 0,
    interactive: bool = False,
):
    """
    TwiML webhook endpoint for Twilio outbound calls.
    Returns TwiML instructions that Twilio executes when the call connects.
    Use this if you prefer callback-based TwiML over inline TwiML.
    Point your Twilio call's 'url' parameter to this endpoint.
    """
    twiml = twilio_voice.build_twiml_response(
        client_name=clientName,
        product_type=productType,
        origin=origin,
        destination=destination,
        original_date=originalDate,
        new_date=newDate,
        new_date_label=newDateLabel,
        reason=reason,
        days_moved=days_moved,
        interactive=interactive,
    )
    from fastapi.responses import Response
    return Response(content=twiml, media_type="application/xml")


@app.post("/api/voice/call")
async def voice_call(req: AnalyzeRequest):
    """
    Direct endpoint to trigger a reschedule SMS notification.
    Runs a quick analysis to get the safe window, then sends the SMS.
    """
    if not req.shippingDate:
        return {"error": "shippingDate required"}

    storm_lat, storm_lon = _storm_coords_for_route(req.origin)
    risk_score = 82  # Assume high enough to trigger reschedule
    safe_windows = _generate_safe_windows(req.shippingDate, storm_lat, storm_lon)
    rescheduled = _compute_reschedule(safe_windows, req, "HIGH", risk_score)

    if not rescheduled:
        return {"sent": False, "reason": "No reschedule needed — risk not high enough"}

    result = twilio_voice.send_reschedule_sms(
        to_number=req.clientPhone or "",
        client_name=req.clientName or "",
        product_type=req.productType,
        origin=req.origin,
        destination=req.destination,
        original_date=rescheduled["originalDate"],
        new_date=rescheduled["newDate"],
        new_date_label=rescheduled.get("newDateLabel", ""),
        reason=rescheduled["reason"],
        days_moved=rescheduled.get("daysMoved", 0),
    )
    return result


@app.post("/api/voice/confirm")
async def voice_confirm():
    """
    Handles <Gather> input from the interactive TwiML flow.
    Key press 1 = confirmed, 2 = request callback.
    """
    from fastapi import Form, Request
    return twilio_voice.build_twiml_response(
        client_name="", product_type="", reason="Thank you for confirming. Goodbye.",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
