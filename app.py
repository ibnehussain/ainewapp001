"""
app.py — Flask application entrypoint.

Serves the static frontend and registers the weather API blueprint.

Run locally:
    python app.py

Run in production (Gunicorn):
    gunicorn app:app --bind 0.0.0.0:5000
"""

import os
from flask import Flask, send_from_directory

import config
from routes.weather import weather_bp

# ── App factory ──────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="/static")

# ── Register blueprints ──────────────────────────────────────────────────────
app.register_blueprint(weather_bp)

# ── Frontend route ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Serve the dashboard HTML from the static folder."""
    return send_from_directory(app.static_folder, "index.html")


# ── Dev server entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=config.FLASK_DEBUG, port=port)
