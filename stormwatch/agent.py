import asyncio
import json
import time
from datetime import datetime
from uuid import uuid4

from config import (
    AGENT_POLL_INTERVAL,
    THREAT_RADIUS_KM,
    DEMO_MODE,
    LLM_API_KEY,
)

from db.clickhouse import insert_weather_events, command
from ingest.weather import poll as weather_poll
from detect.threats import scan_threats, get_historical_matches, get_route_impact, resolve_region
from analyze.pioneer import extract as pioneer_extract
from analyze.llm import assess as llm_assess
from analyze.senso import query as senso_query
from alert.composio import send_alert
from tracing.langfuse import create_trace


class AgentLoop:
    def __init__(self, ws_manager=None):
        self.ws_manager = ws_manager
        self.cycle = 0
        self.running = False
        self.detection_history: dict[str, float] = {}
        self.metrics = {
            "routes_monitored": 8,
            "threats_detected": 0,
            "total_detection_time_ms": 0,
            "detection_count": 0,
            "total_cargo_value": 80_000_000,
        }

    async def start(self):
        self.running = True
        print(f"\n{'='*50}")
        print("  LUMIN AGENT LOOP STARTING")
        print(f"  Demo mode: {DEMO_MODE}")
        print(f"  Poll interval: {AGENT_POLL_INTERVAL}s")
        print(f"  Threat radius: {THREAT_RADIUS_KM}km")
        print(f"{'='*50}\n")

        while self.running:
            await self._tick()
            await asyncio.sleep(AGENT_POLL_INTERVAL)

    async def stop(self):
        self.running = False

    async def _tick(self):
        self.cycle += 1
        cycle_start = time.time()

        # STEP 1: Ingest
        await self._log("agent_log", f"Cycle {self.cycle}: Ingesting weather data...")
        events = await weather_poll(demo=DEMO_MODE, cycle=self.cycle)
        if events:
            insert_weather_events([e for e in events if e["severity"] in ("severe", "extreme")])
            await self._log("agent_log", f"  ✓ Ingested {len(events)} observations")

        # STEP 2: Detect
        await self._log("agent_log", "Scanning for threats...")
        detect_start = time.time()
        threats = scan_threats()
        detect_ms = (time.time() - detect_start) * 1000

        if not threats:
            await self._log("agent_log", "  ✓ No threats detected")
            await self._update_metrics(detect_ms, 0)
            return

        await self._log("agent_log", f"  ⚠️  {len(threats)} threat(s) detected!")
        detected_ids = set()

        for threat in threats:
            event_id = threat.get("event_id", "")
            if event_id in detected_ids:
                continue
            detected_ids.add(event_id)

            # Dedup: skip if assessed within 5 min
            if event_id in self.detection_history:
                if time.time() - self.detection_history[event_id] < 300:
                    continue
            self.detection_history[event_id] = time.time()

            # Create trace
            trace = create_trace("risk-assessment")

            await self._log("threat_detected", {
                "event_type": threat["event_type"],
                "severity": threat["severity"],
                "route_id": threat["route_id"],
                "vessel_name": threat["vessel_name"],
                "distance_km": round(threat["distance_km"], 1),
                "storm_lat": threat["storm_lat"],
                "storm_lon": threat["storm_lon"],
                "description": threat["description"],
                "cargo_value_usd": threat["cargo_value_usd"],
            })

            # STEP 3: Extract entities
            await self._log("agent_log", f"  Extracting entities from weather bulletin...")
            entities = await pioneer_extract(threat.get("description", ""))
            trace.span(
                name="entity-extraction",
                input_data={"bulletin": threat.get("description", "")},
                output_data=entities.to_dict(),
            )
            await self._log("entity_extracted", entities.to_dict())

            # STEP 4: Query knowledge base
            await self._log("agent_log", "  Querying knowledge base...")
            region = resolve_region(threat["storm_lat"], threat["storm_lon"])
            kb_query = (
                f"What is the typical impact of a {entities.category} "
                f"{threat['event_type']} in {entities.affected_area or region}?"
            )
            kb_context = senso_query(kb_query, demo=DEMO_MODE)
            trace.span(name="knowledge-lookup", output_data={"context": kb_context})

            # STEP 5: Get historical matches and route impact
            historical = get_historical_matches(threat["event_type"], region)
            impact = get_route_impact([threat["route_id"]])

            # STEP 6: LLM Risk Assessment
            await self._log("agent_log", "  Generating risk assessment...")
            entities_dict = entities.to_dict()
            assessment = await llm_assess(threat, entities_dict, kb_context, historical, impact)
            trace.generation(
                name="risk-reasoning",
                input_data={
                    "threat": threat.get("event_id"),
                    "entities": entities_dict,
                },
                output_data=assessment.to_dict(),
            )
            trace.end()

            await self._log("risk_assessment", assessment.to_dict())

            # STEP 7: Store in ClickHouse
            assessment_id = str(uuid4())
            try:
                command(f"""
                    INSERT INTO risk_assessments VALUES (
                        '{assessment_id}',
                        now(),
                        '{threat["event_id"]}',
                        [{', '.join(f"'{r['route_id']}'" for r in assessment.affected_routes)}],
                        '{assessment.risk_level}',
                        {max(r.get('estimated_delay_hours', 0) for r in assessment.affected_routes) if assessment.affected_routes else 0},
                        {assessment.total_financial_impact_usd},
                        '{assessment.recommendation.replace("'", "''")}',
                        '{trace.id}'
                    )
                """)
            except Exception as e:
                print(f"  Failed to store assessment: {e}")

            # STEP 8: Alert
            await self._log("agent_log", f"  Risk level: {assessment.risk_level.upper()}")
            if assessment.risk_level in ("high", "critical"):
                await self._log("agent_log", "  🚨 Sending alert via Composio...")
                await send_alert(assessment.to_dict(), threat)

            # Metric: count threats seen
            self.metrics["threats_detected"] += 1

        await self._update_metrics(detect_ms, len(threats))

    async def _log(self, msg_type: str, data):
        payload = json.dumps({"type": msg_type, "data": data, "timestamp": datetime.utcnow().isoformat()})
        print(f"[AGENT] {msg_type}: {str(data)[:120]}")
        if self.ws_manager:
            await self.ws_manager.broadcast(payload)

    async def _update_metrics(self, detect_ms: float, threat_count: int):
        if self.metrics["detection_count"] < 100:
            self.metrics["total_detection_time_ms"] += detect_ms
            self.metrics["detection_count"] += 1

        avg_time = self.metrics["total_detection_time_ms"] / max(self.metrics["detection_count"], 1)
        await self._log("metrics_update", {
            "routes_monitored": self.metrics["routes_monitored"],
            "threats_detected": self.metrics["threats_detected"],
            "avg_detection_time_ms": round(avg_time, 0),
            "total_cargo_value": self.metrics["total_cargo_value"],
            "cycle": self.cycle,
        })
