"""
config.py — Application configuration loaded from environment variables.

Usage:
    import config
    key = config.OWM_API_KEY
"""

import os
from dotenv import load_dotenv

# Load .env file when present (local development); no-op in production
load_dotenv()

# ── OpenWeatherMap ───────────────────────────────────────────
OWM_API_KEY: str  = os.environ.get("OWM_API_KEY", "")
OWM_BASE_URL: str = "https://api.openweathermap.org/data/2.5"

# ── Request behaviour ────────────────────────────────────────
# Seconds to wait before treating an OWM request as timed-out
REQUEST_TIMEOUT: int = int(os.environ.get("REQUEST_TIMEOUT", "10"))

# ── Flask ────────────────────────────────────────────────────
FLASK_DEBUG: bool = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
