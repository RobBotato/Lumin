import json
import re
import time
from dataclasses import dataclass, field

import httpx

from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL, TRUEFOUNDRY_GATEWAY_URL, TRUEFOUNDRY_API_KEY


@dataclass
class RiskAssessment:
    risk_level: str = "low"
    summary: str = ""
    affected_routes: list[dict] = field(default_factory=list)
    total_financial_impact_usd: int = 0
    recommendation: str = ""
    confidence: float = 0.5
    reasoning: str = ""
    needs_human_review: bool = False

    def to_dict(self) -> dict:
        return {
            "risk_level": self.risk_level,
            "summary": self.summary,
            "affected_routes": self.affected_routes,
            "total_financial_impact_usd": self.total_financial_impact_usd,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "needs_human_review": self.needs_human_review,
        }


SYSTEM_PROMPT = """You are Stormwatch, an autonomous supply chain risk assessment agent.
Analyze weather threats to active shipping routes and generate structured risk assessments.

Given:
- Extracted weather entities (storm name, category, wind speed, location, affected area)
- Affected shipping routes with cargo values and vessel names
- Historical disruption patterns from the knowledge base
- Port vulnerability scores

Generate a JSON risk assessment. Rules:
- Always cite historical precedents when available
- Never recommend abandoning cargo
- Financial estimates must be grounded in historical data, not invented
- If confidence is below 0.5, flag as "needs human review"

Return ONLY valid JSON, no markdown fences."""


def build_user_prompt(threat: dict, entities: dict, kb_context: str, historical: list[dict], impact: dict) -> str:
    parts = [
        "## Current Threat",
        f"Event Type: {threat.get('event_type', 'unknown')}",
        f"Severity: {threat.get('severity', 'unknown')}",
        f"Location: ({threat.get('storm_lat', '?')}, {threat.get('storm_lon', '?')})",
        f"Distance to route: {threat.get('distance_km', '?'):.1f} km",
        f"Weather Bulletin: {threat.get('description', '')}",
        f"Wind Speed: {threat.get('wind_speed_kmh', '?')} km/h",
        "",
        "## Extracted Entities",
    ]
    for key, val in entities.items():
        if val:
            parts.append(f"- {key}: {val}")

    parts += [
        "",
        "## Affected Route",
        f"Route ID: {threat.get('route_id', '')}",
        f"Vessel: {threat.get('vessel_name', '')}",
        f"Destination: {threat.get('destination_port', '')}",
        f"Cargo Value: ${threat.get('cargo_value_usd', 0):,}",
    ]

    if impact:
        parts += [
            "",
            "## Impact Summary",
            f"Routes Affected: {impact.get('routes_affected', 1)}",
            f"Total Cargo at Risk: ${impact.get('total_cargo_at_risk', 0):,}",
            f"Vessels: {', '.join(impact.get('vessels', []))}",
        ]

    if kb_context:
        parts += ["", "## Knowledge Base Context", kb_context]

    if historical:
        parts += ["", "## Historical Precedents"]
        for h in historical[:3]:
            parts += [
                f"- {h['event_name']}: {h.get('avg_delay_days', '?')} days delay, "
                f"${h.get('estimated_cost_usd', 0):,} impact. {h.get('lessons', '')}"
            ]

    parts += [
        "",
        "Generate a JSON risk assessment with these fields:",
        "{",
        '  "risk_level": "low|medium|high|critical",',
        '  "summary": "2-sentence summary",',
        '  "affected_routes": [{ "route_id": "...", "vessel_name": "...", "cargo_value_usd": 0, "estimated_delay_hours": 0, "financial_impact_usd": 0 }],',
        '  "total_financial_impact_usd": 0,',
        '  "recommendation": "actionable recommendation",',
        '  "confidence": 0.0-1.0,',
        '  "reasoning": "step-by-step reasoning citing historical patterns"',
        "}",
        "",
        "Return ONLY the JSON.",
    ]
    return "\n".join(parts)


async def assess(threat: dict, entities: dict, kb_context: str = "",
                 historical: list[dict] | None = None,
                 impact: dict | None = None,
                 system_prompt: str | None = None) -> RiskAssessment:
    historical = historical or []
    prompt = build_user_prompt(threat, entities, kb_context, historical, impact)

    response = await _call_llm(system_prompt or SYSTEM_PROMPT, prompt)
    return _parse_assessment(response)


async def _call_llm(system: str, user: str) -> str:
    # Try TrueFoundry first, fall back to OpenRouter
    endpoints = []

    if TRUEFOUNDRY_GATEWAY_URL and TRUEFOUNDRY_API_KEY:
        endpoints.append((TRUEFOUNDRY_GATEWAY_URL.rstrip("/"), TRUEFOUNDRY_API_KEY, LLM_MODEL))

    if LLM_BASE_URL and LLM_API_KEY:
        endpoints.append((LLM_BASE_URL.rstrip("/"), LLM_API_KEY, LLM_MODEL))

    for base_url, api_key, model in endpoints:
        result = await _try_endpoint(base_url, api_key, model, system, user)
        if result:
            return result

    return "{}"


async def _try_endpoint(base_url: str, api_key: str, model: str, system: str, user: str) -> str | None:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 2000,
        "temperature": 0.3,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return content
            else:
                print(f"LLM {base_url[:40]}... status {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"LLM call to {base_url[:40]}... failed: {e}")

    return None


def _parse_assessment(response: str) -> RiskAssessment:
    # Tier 1: Direct parse
    try:
        data = json.loads(response)
        return _build_from_dict(data)
    except json.JSONDecodeError:
        pass

    # Tier 2: Extract from markdown code fence
    m = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
    if m:
        try:
            data = json.loads(m.group(1))
            return _build_from_dict(data)
        except json.JSONDecodeError:
            pass

    # Tier 3: Find first balanced JSON object
    m = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
    if m:
        try:
            data = json.loads(m.group(0))
            return _build_from_dict(data)
        except json.JSONDecodeError:
            pass

    # Fallback: return minimal assessment from response
    return RiskAssessment(
        risk_level="medium",
        summary=response[:200],
        confidence=0.3,
        needs_human_review=True,
        recommendation="Unable to parse assessment. Manual review required.",
    )


def _build_from_dict(data: dict) -> RiskAssessment:
    return RiskAssessment(
        risk_level=data.get("risk_level", "medium"),
        summary=data.get("summary", ""),
        affected_routes=data.get("affected_routes", []),
        total_financial_impact_usd=data.get("total_financial_impact_usd", 0),
        recommendation=data.get("recommendation", ""),
        confidence=float(data.get("confidence", 0.5)),
        reasoning=data.get("reasoning", ""),
        needs_human_review=data.get("confidence", 0.5) < 0.5,
    )
