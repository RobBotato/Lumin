<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/next.js-15.5-black" alt="Next.js 15.5">
  <img src="https://img.shields.io/badge/fastapi-0.110%2B-teal" alt="FastAPI">
  <img src="https://img.shields.io/badge/clickhouse-analytical-orange" alt="ClickHouse">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT">
</p>

# ⚡ Lumin Stormwatch

**AI-powered supply chain weather intelligence.** Detects storms, assesses risk against cargo sensitivity, auto-reschedules shipments on Google Calendar, and notifies clients via email — all through a multi-agent pipeline.

---

## What it does

1. **Ingests** a shipment (product type, origin, destination, date)
2. **Detects** active weather threats along shipping corridors using ClickHouse analytical queries
3. **Extracts** storm entities (name, category, wind speed, location) via Pioneer NLP
4. **Assesses** risk using LLM reasoning (TrueFoundry / OpenRouter) grounded in a local knowledge base of historical disruption patterns
5. **Reschedules** shipments automatically — cancels the original Google Calendar event and creates a new one on a safe date
6. **Notifies** the client via formatted HTML email
7. **Tracks** everything through Langfuse observability and a real-time WebSocket dashboard

---

## Architecture

```
┌──────────────┐     ┌──────────────────────────────────────┐
│  Next.js 15  │────▶│         FastAPI Backend              │
│  Frontend    │     │                                      │
│  :3000       │     │  /api/analyze    Risk pipeline       │
│              │     │  /api/calendar   .ics export          │
│              │◀────│  /api/auth       Google OAuth         │
│              │ WS  │  /ws             Real-time agent feed │
└──────────────┘     └──────────┬───────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
   │  ClickHouse  │    │  LLM Gateway │    │  Google Calendar │
   │  Weather DB  │    │  TrueFoundry │    │  OAuth2 API      │
   │  Routes      │    │  OpenRouter  │    │  Cancel/Create   │
   └──────────────┘    └──────────────┘    └──────────────────┘
          │                     │                     │
          ▼                     ▼                     ▼
   ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
   │  Pioneer NLP │    │  Langfuse    │    │  SMTP Email      │
   │  NER Engine  │    │  Tracing     │    │  Notifications   │
   └──────────────┘    └──────────────┘    └──────────────────┘
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-agent pipeline** | Shipment ingest → weather detection → entity extraction → knowledge lookup → LLM assessment → calendar update → email notification |
| **Real-time dashboard** | WebSocket-powered agent timeline, risk score card, threat matrix, financial breakdown, port weather, safe shipping windows |
| **Google Calendar sync** | OAuth2 integration — reads shipment events, cancels original dates (crossed out), creates rescheduled events |
| **Client email notifications** | SMTP-based HTML emails with styled delivery cards, sent automatically on reschedule |
| **LLM risk assessment** | Structured JSON risk analysis with confidence scoring, fallback between TrueFoundry and OpenRouter |
| **Langfuse observability** | Full tracing across entity extraction, knowledge lookup, and LLM generation steps |
| **Historical knowledge base** | Local markdown files covering hurricane patterns, port profiles, and response procedures |
| **Responsive design** | Dark-themed dashboard with glass morphism cards, animated pipeline timeline, and print-friendly layout |

---

## APIs & Integrations

| Service | Purpose | Config |
|---------|---------|--------|
| **ClickHouse Cloud** | Analytical database for weather events, shipping routes, ports | `CLICKHOUSE_*` |
| **TrueFoundry** | LLM gateway (primary) | `TRUEFOUNDRY_*` |
| **OpenRouter** | LLM gateway (fallback) | `LLM_*` |
| **Pioneer** | NLP entity extraction from weather bulletins | `PIONEER_*` |
| **Google Calendar** | OAuth2 — read, cancel, and create shipment events | `GOOGLE_*` |
| **Langfuse** | LLM tracing and observability | `LANGFUSE_*` |
| **OpenWeatherMap** | Real-time weather data (optional) | `OWM_API_KEY` |
| **Composio** | Slack alerting for high-risk assessments | `COMPOSIO_*` |
| **SMTP (Gmail)** | Client email notifications | `EMAIL_*` |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+
- ClickHouse Cloud account (free tier works)
- A Google Cloud project with Calendar API enabled (for calendar integration)
- SMTP credentials (e.g., Gmail with an app password) for email notifications

### Backend

```bash
cd stormwatch

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env    # then edit .env with your credentials

# Start the server
python main.py
```

The API runs on **http://localhost:8080**.

### Frontend

```bash
cd stormwatch/frontend

npm install
npm run dev
```

Open **http://localhost:3000**.

### Environment Variables

Create `stormwatch/.env` with the following:

```env
# ClickHouse Cloud
CLICKHOUSE_HOST=your-host.clickhouse.cloud
CLICKHOUSE_PORT=8443
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your-password
CLICKHOUSE_SECURE=true

# LLM
LLM_API_KEY=sk-or-v1-...
LLM_MODEL=anthropic/claude-sonnet-4-6
LLM_BASE_URL=https://openrouter.ai/api/v1

# Google Calendar OAuth2
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8080/api/auth/google/callback

# Pioneer NLP
PIONEER_API_KEY=pio_sk_...
PIONEER_MODEL_ID=fastino/gliner2-base-v1

# TrueFoundry
TRUEFOUNDRY_GATEWAY_URL=https://gateway.truefoundry.ai
TRUEFOUNDRY_API_KEY=...

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com

# Email notifications
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=you@gmail.com
EMAIL_PASSWORD=your-app-password

# Demo mode (use simulated data when APIs aren't configured)
DEMO_MODE=true
```

---

## Project Structure

```
stormwatch/
├── main.py                    # FastAPI server, all endpoints
├── config.py                  # Environment variable loading
├── requirements.txt           # Python dependencies
├── .env                       # Credentials (gitignored)
│
├── agent.py                   # Autonomous agent loop (poll → detect → assess)
├── ingest/weather.py          # OpenWeatherMap data ingestion
├── detect/threats.py          # ClickHouse threat detection queries
├── analyze/
│   ├── llm.py                 # LLM risk assessment (TrueFoundry / OpenRouter)
│   ├── pioneer.py             # NLP entity extraction
│   └── senso.py               # Local knowledge base search
├── alert/composio.py          # Slack alerting via Composio
├── tracing/langfuse.py        # Langfuse observability traces
│
├── db/
│   ├── clickhouse.py          # ClickHouse client + queries
│   ├── schema.py              # Table definitions
│   └── seed.py                # Seed data (routes, ports, historical events)
│
├── integrations/
│   ├── google_calendar.py     # OAuth2, event CRUD, cancel + reschedule
│   └── twilio_voice.py        # Email/SMS notification dispatch
│
├── kb/                        # Knowledge base (markdown files)
│   ├── disruption-patterns/   # Hurricane, monsoon, typhoon patterns
│   ├── port-profiles/         # LA, Shanghai, Singapore, etc.
│   └── response-procedures/   # Rerouting, insurance, notification
│
├── frontend/                  # Next.js app
│   ├── app/                   # Routes (/, /analyze, /dashboard)
│   ├── components/
│   │   ├── ui/                # Primitives (button, card, input, select, etc.)
│   │   ├── landing/           # Landing page sections
│   │   ├── analyze/           # Shipment form
│   │   └── dashboard/         # Risk score, threats, recommendations, agent timeline
│   └── lib/
│       ├── types.ts           # Domain types (UI ↔ API contract)
│       ├── mock-data.ts        # Mock scenarios and pipeline steps
│       ├── services/weather-risk.ts  # API integration point
│       └── presentation.ts    # Risk colors, badges, icon mappings
│
└── forecastcart.html          # Standalone landing page demo
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/analyze` | Run the full risk analysis pipeline |
| `GET` | `/api/calendar-event` | Generate `.ics` file for rescheduled shipment |
| `GET` | `/api/calendar/shipments` | List shipments synced from Google Calendar |
| `GET` | `/api/auth/google` | Google OAuth2 redirect |
| `GET` | `/api/auth/google/callback` | OAuth2 callback handler |
| `GET` | `/api/auth/google/status` | Connection status |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/metrics` | Agent loop metrics |
| `GET` | `/api/demo/trigger-storm` | Manual demo trigger |
| `GET` | `/api/voice/twiml` | TwiML webhook (legacy voice) |
| `POST` | `/api/voice/call` | Direct notification endpoint |
| `WebSocket` | `/ws` | Real-time agent events |

---

## License

MIT
