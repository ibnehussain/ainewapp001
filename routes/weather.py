"""
routes/weather.py — Flask Blueprint for the /api/weather endpoint.

Registered on the app in app.py.
"""

from flask import Blueprint, request, jsonify
from utils.weather_service import fetch_weather, CityNotFoundError, WeatherServiceError

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/api/weather", methods=["GET"])
def get_weather():
    """
    GET /api/weather?city=<name>

    Query parameters:
        city (str, required): City name to look up.

    Responses:
        200  Normalized weather JSON.
        400  Missing or empty city parameter.
        404  City not recognised by OpenWeatherMap.
        502  Upstream weather service failure or misconfiguration.
    """
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "A city name is required."}), 400

    try:
        data = fetch_weather(city)
        return jsonify(data), 200

    except CityNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404

    except WeatherServiceError as exc:
        return jsonify({"error": str(exc)}), 502
