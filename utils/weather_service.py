"""
utils/weather_service.py — OpenWeatherMap integration and response normalization.

Responsibilities:
  - Call the OWM current-weather endpoint
  - Apply timeouts and handle network-level errors
  - Normalize the raw OWM payload into an app-owned shape
  - Raise typed exceptions so the route layer can return correct HTTP statuses
  - Return realistic dummy data when OWM_API_KEY is not configured

The frontend (app.js) expects the normalized shape:
  {
    city, country, temp_c, feels_like_c, humidity,
    condition, wind_speed_mps, visibility_m, timestamp
  }
"""

import random
from datetime import datetime, timezone
import requests
import config


# ── Dummy data ───────────────────────────────────────────────────────────────
# Realistic per-city defaults used when no OWM API key is configured.
# City keys are lowercase for case-insensitive lookup; the fallback entry
# handles any city name not explicitly listed.

_DUMMY_DATA: dict[str, dict] = {
    "london": {
        "city": "London", "country": "GB",
        "temp_c": 14.2, "feels_like_c": 12.5, "humidity": 78,
        "condition": "Overcast clouds", "wind_speed_mps": 5.1,
        "visibility_m": 9000,
    },
    "new york": {
        "city": "New York", "country": "US",
        "temp_c": 22.8, "feels_like_c": 21.4, "humidity": 55,
        "condition": "Clear sky", "wind_speed_mps": 3.6,
        "visibility_m": 10000,
    },
    "tokyo": {
        "city": "Tokyo", "country": "JP",
        "temp_c": 28.5, "feels_like_c": 31.0, "humidity": 82,
        "condition": "Light rain", "wind_speed_mps": 2.8,
        "visibility_m": 7000,
    },
    "paris": {
        "city": "Paris", "country": "FR",
        "temp_c": 18.3, "feels_like_c": 17.1, "humidity": 65,
        "condition": "Partly cloudy", "wind_speed_mps": 4.2,
        "visibility_m": 10000,
    },
    "dubai": {
        "city": "Dubai", "country": "AE",
        "temp_c": 38.0, "feels_like_c": 42.5, "humidity": 38,
        "condition": "Sunny", "wind_speed_mps": 3.0,
        "visibility_m": 10000,
    },
    "sydney": {
        "city": "Sydney", "country": "AU",
        "temp_c": 20.1, "feels_like_c": 19.3, "humidity": 68,
        "condition": "Scattered clouds", "wind_speed_mps": 6.5,
        "visibility_m": 9500,
    },
    "toronto": {
        "city": "Toronto", "country": "CA",
        "temp_c": 16.7, "feels_like_c": 15.2, "humidity": 60,
        "condition": "Mostly cloudy", "wind_speed_mps": 4.8,
        "visibility_m": 10000,
    },
    "berlin": {
        "city": "Berlin", "country": "DE",
        "temp_c": 17.4, "feels_like_c": 16.0, "humidity": 70,
        "condition": "Light drizzle", "wind_speed_mps": 3.9,
        "visibility_m": 8000,
    },
    "mumbai": {
        "city": "Mumbai", "country": "IN",
        "temp_c": 31.0, "feels_like_c": 36.0, "humidity": 88,
        "condition": "Humid and hazy", "wind_speed_mps": 2.1,
        "visibility_m": 5000,
    },
    "cape town": {
        "city": "Cape Town", "country": "ZA",
        "temp_c": 16.5, "feels_like_c": 15.8, "humidity": 72,
        "condition": "Windy with clouds", "wind_speed_mps": 8.3,
        "visibility_m": 9000,
    },
}

# Generic fallback — varies slightly on each call to feel dynamic
_FALLBACK_CONDITIONS = [
    "Partly cloudy", "Clear sky", "Scattered clouds",
    "Light breeze", "Overcast", "Sunny intervals",
]


# ── Custom exceptions ────────────────────────────────────────────────────────

class CityNotFoundError(Exception):
    """Raised when OWM reports the city does not exist."""


class WeatherServiceError(Exception):
    """Raised for any other upstream or configuration failure."""


# ── Public API ───────────────────────────────────────────────────────────────

def fetch_weather(city: str) -> dict:
    """
    Fetch current weather for *city* from OpenWeatherMap and return a
    normalized dict.

    When OWM_API_KEY is not set, realistic dummy data is returned so the
    UI can be developed and demoed without a live API key.

    Raises:
        CityNotFoundError:  city name was not recognised by OWM.
        WeatherServiceError: any other failure (timeout, bad key, 5xx, etc.).
    """
    if not config.OWM_API_KEY:
        return _dummy_weather(city)

    url = f"{config.OWM_BASE_URL}/weather"
    params = {
        "q":     city,
        "appid": config.OWM_API_KEY,
        "units": "metric",   # always Celsius; the frontend converts to °F
    }

    raw = _get(url, params)
    return _normalize(raw, city)


# ── Private helpers ──────────────────────────────────────────────────────────

def _dummy_weather(city: str) -> dict:
    """
    Return a realistic dummy weather response for *city*.

    Performs a case-insensitive lookup in _DUMMY_DATA; falls back to a
    generated entry so any city name produces a plausible-looking result.
    The response includes a DEMO_MODE flag so the frontend can optionally
    show a banner informing the developer that live data is not being used.
    """
    key = city.strip().lower()
    base = _DUMMY_DATA.get(key)

    if base:
        data = dict(base)          # shallow copy so originals are unchanged
    else:
        # Generate a plausible generic response for unknown cities
        data = {
            "city":           city.title(),
            "country":        "--",
            "temp_c":         round(random.uniform(5.0, 35.0), 1),
            "feels_like_c":   round(random.uniform(3.0, 37.0), 1),
            "humidity":       random.randint(30, 95),
            "condition":      random.choice(_FALLBACK_CONDITIONS),
            "wind_speed_mps": round(random.uniform(0.5, 10.0), 1),
            "visibility_m":   random.choice([5000, 7000, 9000, 10000]),
        }

    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    data["demo_mode"] = True   # signals the frontend: no real API key in use
    return data


def _get(url: str, params: dict) -> dict:
    """Make a GET request to OWM and return the parsed JSON body."""
    try:
        response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        raise WeatherServiceError(
            "The weather service did not respond in time. Please try again."
        )
    except requests.exceptions.RequestException as exc:
        raise WeatherServiceError(
            f"Could not reach the weather service: {exc}"
        ) from exc

    _raise_for_status(response, params.get("q", ""))
    return response.json()


def _raise_for_status(response: requests.Response, city: str) -> None:
    """Convert OWM error status codes into typed exceptions."""
    if response.status_code == 404:
        raise CityNotFoundError(f"City '{city}' was not found.")

    if response.status_code == 401:
        raise WeatherServiceError(
            "Invalid API key. Check your OWM_API_KEY configuration."
        )

    if response.status_code == 429:
        raise WeatherServiceError(
            "Weather API rate limit exceeded. Please wait a moment and try again."
        )

    if not response.ok:
        raise WeatherServiceError(
            f"Weather service returned an unexpected error "
            f"(HTTP {response.status_code})."
        )


def _normalize(data: dict, city_fallback: str) -> dict:
    """
    Map a raw OWM 'current weather' payload to the app-owned response shape.

    All temperature values are kept in Celsius; the browser converts for °F.
    """
    main    = data.get("main", {})
    wind    = data.get("wind", {})
    weather = data.get("weather", [{}])
    sys     = data.get("sys", {})

    return {
        "city":           data.get("name") or city_fallback,
        "country":        sys.get("country", ""),
        "temp_c":         round(main.get("temp", 0), 1),
        "feels_like_c":   round(main.get("feels_like", 0), 1),
        "humidity":       main.get("humidity", 0),          # percent
        "condition":      weather[0].get("description", "").capitalize(),
        "wind_speed_mps": round(wind.get("speed", 0), 1),  # m/s
        "visibility_m":   data.get("visibility", 0),        # metres
        "timestamp":      datetime.now(timezone.utc).isoformat(),
    }
