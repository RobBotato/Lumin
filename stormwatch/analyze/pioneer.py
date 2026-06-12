import re
from dataclasses import dataclass, field

from config import PIONEER_API_KEY, PIONEER_MODEL_ID


@dataclass
class Entities:
    storm_name: str = ""
    category: str = ""
    wind_speed: str = ""
    location: str = ""
    affected_area: str = ""
    duration: str = ""
    direction: str = ""
    raw: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "storm_name": self.storm_name,
            "category": self.category,
            "wind_speed": self.wind_speed,
            "location": self.location,
            "affected_area": self.affected_area,
            "duration": self.duration,
            "direction": self.direction,
        }


async def extract(text: str) -> Entities:
    if PIONEER_API_KEY and PIONEER_MODEL_ID:
        return await _pioneer_extract(text)
    return _regex_extract(text)


async def _pioneer_extract(text: str) -> Entities:
    import httpx

    entity_types = [
        "storm_name", "category", "wind_speed",
        "location", "affected_area", "duration", "direction",
    ]
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.pioneer.ai/inference",
                headers={
                    "Authorization": f"Bearer {PIONEER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model_id": PIONEER_MODEL_ID,
                    "text": text,
                    "schema": {"entities": entity_types},
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                result = data.get("result", {}).get("data", {}).get("entities", {})
                return _parse_pioneer_response(result)
    except Exception as e:
        print(f"Pioneer API error: {e}")

    return _regex_extract(text)


def _regex_extract(text: str) -> Entities:
    entities = Entities(raw=[])

    storm_patterns = [
        r"(?:Tropical\s+)?(?:Storm|Typhoon|Hurricane|Cyclone)\s+([A-Z][a-z]+)",
        r"named\s+([A-Z][a-z]+)",
    ]
    for pat in storm_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            entities.storm_name = m.group(1)
            break

    cat_match = re.search(r"Category\s+(\d+)", text, re.IGNORECASE)
    if cat_match:
        entities.category = f"Category {cat_match.group(1)}"

    wind_match = re.search(r"(\d+)\s*(?:mph|km/h|knots)", text, re.IGNORECASE)
    if wind_match:
        entities.wind_speed = f"{wind_match.group(1)} {wind_match.group(0).replace(wind_match.group(1), '').strip()}"

    loc_patterns = [
        r"(?:near|at|off)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"make landfall\s+(?:near|at|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
    ]
    for pat in loc_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            entities.location = m.group(1)
            break

    area_patterns = [
        r"(?:affecting|in)\s+(?:shipping lanes in\s+)?(?:the\s+)?((?:[A-Z][a-z]+\s*)+)",
    ]
    for pat in area_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m and m.group(1).strip():
            candidate = m.group(1).strip()
            if len(candidate) > 4 and not candidate.startswith("through"):
                entities.affected_area = candidate
                break

    dur_match = re.search(r"(?:through|until)\s+([A-Z][a-z]+day)", text, re.IGNORECASE)
    if dur_match:
        entities.duration = dur_match.group(0)

    dir_match = re.search(r"(?:moving|heading|tracking)\s+([a-z]+(?:-?[a-z]+)?)", text, re.IGNORECASE)
    if dir_match:
        entities.direction = dir_match.group(1)

    return entities


def _parse_pioneer_response(entities_map: dict) -> Entities:
    entities = Entities(raw=entities_map)
    for label, matches in entities_map.items():
        if not matches:
            continue
        text_val = matches[0]["text"] if isinstance(matches, list) else matches
        if label == "storm_name":
            entities.storm_name = text_val
        elif label == "category":
            entities.category = text_val
        elif label == "wind_speed":
            entities.wind_speed = text_val
        elif label == "location":
            entities.location = text_val
        elif label == "affected_area":
            entities.affected_area = text_val
        elif label == "duration":
            entities.duration = text_val
        elif label == "direction":
            entities.direction = text_val
    return entities


def _parse_entities(api_response: list[dict]) -> Entities:
    entities = Entities(raw=api_response)
    for ent in api_response:
        label = ent.get("label", "")
        text_val = ent.get("text", "")
        if label == "storm_name":
            entities.storm_name = text_val
        elif label == "category":
            entities.category = text_val
        elif label == "wind_speed":
            entities.wind_speed = text_val
        elif label == "location":
            entities.location = text_val
        elif label == "affected_area":
            entities.affected_area = text_val
        elif label == "duration":
            entities.duration = text_val
        elif label == "direction":
            entities.direction = text_val
    return entities
