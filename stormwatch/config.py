import os
from dotenv import load_dotenv

load_dotenv()

# ClickHouse
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8443"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_SECURE = os.getenv("CLICKHOUSE_SECURE", "true").lower() == "true"

# OpenWeatherMap
OWM_API_KEY = os.getenv("OWM_API_KEY", "")

# Pioneer
PIONEER_API_KEY = os.getenv("PIONEER_API_KEY", "")
PIONEER_MODEL_ID = os.getenv("PIONEER_MODEL_ID", "")

# Senso.ai
SENSO_KB_PATH = os.getenv("SENSO_KB_PATH", "./kb")

# TrueFoundry
TRUEFOUNDRY_GATEWAY_URL = os.getenv("TRUEFOUNDRY_GATEWAY_URL", "")
TRUEFOUNDRY_API_KEY = os.getenv("TRUEFOUNDRY_API_KEY", "")

# Composio
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "")

# Google Calendar
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/api/auth/google/callback")

# Langfuse
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# LLM
LLM_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-6")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")

# Agent
AGENT_POLL_INTERVAL = int(os.getenv("AGENT_POLL_INTERVAL", "30"))
THREAT_RADIUS_KM = int(os.getenv("THREAT_RADIUS_KM", "300"))

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# Textbelt (free SMS fallback, no account needed. $0.03/msg with key)
TEXTBELT_KEY = os.getenv("TEXTBELT_KEY", "")

# Email-to-SMS gateway
EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))

# Demo mode: use simulated data when APIs aren't configured
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
