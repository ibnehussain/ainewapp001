## Architecture Diagram and Data Flow — Weather Dashboard Flask App

### Architecture Diagram

```mermaid
graph TB
    subgraph Browser["Browser (Client)"]
        UI["index.html\nDashboard UI"]
        CSS["style.css\nResponsive Styles"]
        JS["app.js\nfetch · render · toggle"]
    end

    subgraph Flask["Flask Backend (Server)"]
        STATIC["Static File Server\nGET /"]
        ROUTE["Weather Route\nGET /api/weather?city=&unit="]
        SERVICE["weather_service.py\nProxy · Normalize · Validate"]
        CONFIG["config.py\nAPI Key from .env"]
    end

    subgraph OWM["OpenWeatherMap API"]
        OWMAPI["Current Weather Endpoint\napi.openweathermap.org/data/2.5/weather"]
    end

    UI -->|"user submits city"| JS
    JS -->|"GET /api/weather?city=London&unit=C"| ROUTE
    ROUTE --> SERVICE
    SERVICE --> CONFIG
    SERVICE -->|"GET /weather?q=London&appid=KEY&units=metric"| OWMAPI
    OWMAPI -->|"raw JSON payload"| SERVICE
    SERVICE -->|"normalized JSON"| ROUTE
    ROUTE -->|"{ city, temp, condition, humidity, feelsLike, unit }"| JS
    JS -->|"renders result"| UI
    STATIC -->|"serves HTML/CSS/JS on first load"| Browser
```

---

### Data Flow — Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant FE as Browser<br/>(app.js)
    participant Flask as Flask Backend<br/>(routes/weather.py)
    participant SVC as weather_service.py
    participant OWM as OpenWeatherMap API

    User->>FE: Types city name + submits search
    FE->>FE: Debounce & validate input (non-empty, trim)
    FE->>FE: Show loading indicator
    FE->>Flask: GET /api/weather?city=London&unit=C

    Flask->>Flask: Validate query params (city present)
    Flask->>SVC: fetch_weather(city="London", unit="C")
    SVC->>SVC: Read API key from config (env var)
    SVC->>OWM: GET /data/2.5/weather?q=London&units=metric&appid=KEY

    alt Success
        OWM-->>SVC: 200 raw JSON (provider schema)
        SVC->>SVC: Normalize → app-owned shape
        SVC-->>Flask: { city, temp, feelsLike, humidity, condition, unit }
        Flask-->>FE: 200 JSON response
        FE->>FE: Hide loader, render weather card
        FE-->>User: Displays current weather
    else City not found (OWM 404)
        OWM-->>SVC: 404 { cod: "404" }
        SVC-->>Flask: raise CityNotFoundError
        Flask-->>FE: 404 { error: "City not found" }
        FE-->>User: Shows "City not found" message
    else Upstream failure / timeout
        OWM-->>SVC: 5xx or timeout
        SVC-->>Flask: raise WeatherServiceError
        Flask-->>FE: 502 { error: "Weather service unavailable" }
        FE-->>User: Shows retry-able error state
    end

    Note over User,FE: Unit toggle (C↔F) is client-only —<br/>re-converts last fetched value,<br/>no new network call
```

---

### Key Design Decisions

| Concern | Decision |
|---|---|
| API key location | Only in Flask `config.py` loaded from `.env` — never in the browser |
| Provider schema coupling | `weather_service.py` normalizes before returning — frontend never sees OWM's raw shape |
| Unit toggle | Client-side conversion from the last cached response — avoids a redundant round-trip |
| Error surface | Three distinct failure paths (city not found, service error, timeout) each return a typed JSON error |
| Static assets | Flask serves `index.html`, `style.css`, and `app.js` on first load from the same origin, eliminating CORS entirely |

---

### Normalized JSON Response Contract

**Success — 200**
```json
{
  "city": "London",
  "country": "GB",
  "temp": 15,
  "feelsLike": 12,
  "humidity": 72,
  "condition": "Cloudy",
  "unit": "C",
  "timestamp": "2026-06-16T10:30:00Z"
}
```

**City not found — 404**
```json
{ "error": "City not found" }
```

**Service unavailable — 502**
```json
{ "error": "Weather service unavailable" }
```
