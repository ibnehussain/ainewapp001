## Plan: Weather Dashboard Flask App

Build a production-oriented weather dashboard as a Flask application that serves a static frontend written in HTML, CSS, and JavaScript. Use Flask as both the backend proxy for the weather provider and the app server for the frontend so the deployment model stays simple and the provider API key remains server-side.

**Steps**
1. Phase 1 - Scaffold a single Flask project in the empty workspace at c:\co-pilot\ainewapp001 with a minimal Python app entrypoint, dependency file, environment templates, and folders for static assets and backend modules. This step blocks all later work.
2. Phase 2 - Create the frontend shell inside the Flask-served static layer: a responsive dashboard page, stylesheet, and browser-side JavaScript entrypoint. Keep the first layout focused on the current weather view, city search, and Celsius/Fahrenheit toggle. This depends on step 1.
3. Phase 3 - Add a narrow Flask API surface for the frontend to call, with a current-weather endpoint and, only if needed by the chosen provider flow, a small city search or geocoding endpoint. This depends on step 1.
4. Phase 4 - Implement the provider integration on the backend using a dedicated service module that calls the external weather API, applies timeouts, validates required inputs, and normalizes raw provider payloads into app-owned response shapes. This depends on step 3.
5. Phase 5 - Wire the frontend JavaScript to the Flask endpoints using fetch, then render weather data into the dashboard without page reloads. Keep the unit toggle client-driven for display requests while the backend remains the only layer that knows the provider key. This depends on steps 2 to 4.
6. Phase 6 - Add UX and resilience behavior: loading state, empty state, invalid-city handling, clear API error messages, basic form validation, and debounced search submission to avoid unnecessary requests. This depends on step 5.
7. Phase 7 - Add production-readiness basics on the Flask side: configuration loading from environment variables, separation of routes from provider logic, optional in-memory caching for repeated lookups, and a WSGI-ready run path for deployment. This depends on steps 3 and 4, and can proceed in parallel with step 6.
8. Phase 8 - Document local setup and verify the app end to end: Flask serves the frontend, browser requests hit only Flask, current weather loads correctly for searched cities, the unit toggle behaves consistently, and backend/provider failures surface cleanly. This depends on all prior steps.

**Relevant files**
- c:\co-pilot\ainewapp001\app.py — Flask application entrypoint and top-level app wiring.
- c:\co-pilot\ainewapp001\requirements.txt — Python runtime dependencies such as Flask, requests, and dotenv support.
- c:\co-pilot\ainewapp001\config.py — environment-based configuration and provider settings.
- c:\co-pilot\ainewapp001\.env.example — documented required environment variables without secrets.
- c:\co-pilot\ainewapp001\static\index.html — dashboard markup served by Flask.
- c:\co-pilot\ainewapp001\static\css\style.css — responsive dashboard styling.
- c:\co-pilot\ainewapp001\static\js\app.js — browser-side fetch, rendering, unit toggle, and interaction logic.
- c:\co-pilot\ainewapp001\routes\weather.py — Flask route handlers for weather and optional search endpoints.
- c:\co-pilot\ainewapp001\routes\__init__.py — route package wiring if blueprints are used.
- c:\co-pilot\ainewapp001\utils\weather_service.py — external weather provider integration and response normalization.
- c:\co-pilot\ainewapp001\utils\validators.py — request validation helpers if needed.
- c:\co-pilot\ainewapp001\README.md — local run steps, environment setup, and deployment notes.

**Verification**
1. Install Python dependencies and start the Flask app locally, then confirm the frontend page loads from Flask successfully.
2. Verify the browser fetches weather data from Flask endpoints only and never directly from the third-party weather provider.
3. Verify city search updates the current weather view without a full page reload.
4. Verify the Celsius/Fahrenheit toggle updates displayed values consistently for the same selected city.
5. Force an invalid city or upstream API failure and confirm the app shows a clear error state rather than breaking.
6. Confirm the provider API key exists only in backend environment configuration and is not exposed in frontend files or browser requests.

**Decisions**
- Frontend stack: static HTML, CSS, and JavaScript.
- Backend stack: Flask with Python.
- Project shape: one Flask app serving both backend endpoints and static frontend assets.
- Scope included in v1: current weather, city search, and Celsius/Fahrenheit unit toggle.
- Scope excluded from this first pass: forecast, geolocation, favorites, charts, and radar/maps.
- Deployment posture: production-oriented, so the weather provider key stays server-side behind Flask.
- Architecture preference: normalize third-party provider payloads in backend service code before returning JSON to the frontend.

**Further Considerations**
1. Weather provider selection should be made early. Recommendation: choose one with simple current-conditions and geocoding endpoints plus a reasonable free tier, such as OpenWeather or WeatherAPI.
2. If you later need saved preferences or favorites, decide whether to keep them in browser storage first or introduce a database-backed user model.
3. If forecast support is likely soon, define the backend response shapes so daily or hourly data can be added without changing the frontend fetch pattern.
