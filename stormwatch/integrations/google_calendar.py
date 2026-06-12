"""
Google Calendar integration using OAuth2.
Reads shipment events and modifies/reschedules them when threats are detected.
"""

import json
import os
from datetime import datetime, timedelta

import httpx

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", ".google_token.json")

# Will be populated when config is loaded
GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""
GOOGLE_REDIRECT_URI = "http://localhost:8080/api/auth/google/callback"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def _init_config():
    global GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
    from config import GOOGLE_CLIENT_ID as cid, GOOGLE_CLIENT_SECRET as cs, GOOGLE_REDIRECT_URI as ru
    GOOGLE_CLIENT_ID = cid
    GOOGLE_CLIENT_SECRET = cs
    GOOGLE_REDIRECT_URI = ru


def get_auth_url() -> str:
    _init_config()
    if not GOOGLE_CLIENT_ID:
        return ""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://accounts.google.com/o/oauth2/v2/auth?{qs}"


async def exchange_code(code: str) -> dict:
    """Exchange authorization code for tokens."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI,
            },
        )
        if resp.status_code != 200:
            raise Exception(f"Token exchange failed: {resp.text}")

        data = resp.json()
        data["expires_at"] = (datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))).isoformat()
        _save_token(data)
        return data


def _save_token(data: dict):
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f)


def _load_token() -> dict | None:
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH) as f:
            return json.load(f)
    except Exception:
        return None


async def _get_valid_token() -> str | None:
    """Get a valid access token, refreshing if needed."""
    token = _load_token()
    if not token:
        return None

    # Check if expired
    if token.get("expires_at"):
        try:
            expires = datetime.fromisoformat(token["expires_at"])
            if datetime.utcnow() >= expires:
                token = await _refresh_token(token.get("refresh_token"))
                if not token:
                    return None
        except Exception:
            pass

    return token.get("access_token")


async def _refresh_token(refresh_token: str) -> dict | None:
    """Refresh an expired access token."""
    if not refresh_token:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        data["refresh_token"] = refresh_token
        data["expires_at"] = (datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))).isoformat()
        _save_token(data)
        return data


def is_connected() -> bool:
    """Check if Google Calendar is connected."""
    token = _load_token()
    return token is not None and bool(token.get("access_token"))


async def list_upcoming_events(max_results: int = 10) -> list[dict]:
    """List upcoming shipment events from Google Calendar."""
    token = await _get_valid_token()
    if not token:
        return []

    now = datetime.utcnow().isoformat() + "Z"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "timeMin": now,
                "maxResults": max_results,
                "singleEvents": True,
                "orderBy": "startTime",
                "q": "📦",  # Search for shipment events
            },
        )
        if resp.status_code != 200:
            print(f"Calendar list error: {resp.text[:200]}")
            return []

        events = resp.json().get("items", [])
        shipments = []
        for e in events:
            start = e.get("start", {}).get("date", e.get("start", {}).get("dateTime", ""))[:10]
            shipments.append({
                "id": e.get("id", ""),
                "title": e.get("summary", ""),
                "description": e.get("description", ""),
                "date": start,
                "source": "google_calendar",
                "calendarEventId": e.get("id"),
            })
        return shipments


async def reschedule_event(event_id: str, new_date: str, reason: str = "") -> bool:
    """Move a Google Calendar event to a new date."""
    token = await _get_valid_token()
    if not token:
        return False

    new_start = f"{new_date}"
    new_end_date = datetime.strptime(new_date, "%Y-%m-%d") + timedelta(days=1)
    new_end = new_end_date.strftime("%Y-%m-%d")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.patch(
            f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "start": {"date": new_start},
                "end": {"date": new_end},
                "description": f"RESCHEDULED by Lumin agent.\n{reason}\n\nOriginal event preserved.",
            },
        )
        if resp.status_code == 200:
            print(f"  ✅ Calendar event {event_id} rescheduled to {new_date}")
            return True
        else:
            print(f"  ❌ Calendar reschedule failed: {resp.text[:200]}")
            return False


async def cancel_event(event_id: str, reason: str = "") -> bool:
    """Cancel a Google Calendar event (shows crossed out in calendar)."""
    token = await _get_valid_token()
    if not token:
        return False

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.patch(
            f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "status": "cancelled",
                "description": f"CANCELLED: Original shipment date cancelled due to weather risk.\n{reason}",
            },
        )
        if resp.status_code == 200:
            print(f"  ✅ Calendar event {event_id} cancelled (crossed out)")
            return True
        else:
            print(f"  ❌ Calendar cancel failed: {resp.text[:200]}")
            return False


async def create_shipment_event(title: str, date: str, origin: str, destination: str, notes: str = "") -> str | None:
    """Create a new shipment event in Google Calendar."""
    token = await _get_valid_token()
    if not token:
        return None

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "summary": f"📦 {title} — {origin} → {destination}",
                "description": f"Shipment: {title}\nRoute: {origin} → {destination}\nNotes: {notes}\n\nManaged by Lumin",
                "start": {"date": date},
                "end": {"date": date},
                "transparency": "opaque",
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("id")
        else:
            print(f"Calendar create error: {resp.text[:200]}")
            return None
