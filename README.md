# Weather Dashboard (Flask)

A small Flask app that serves a weather dashboard UI and exposes an API endpoint at `/api/weather`.

## Prerequisites

- Python 3.11+
- An OpenWeatherMap API key

## Run locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy environment template and set your API key:
   ```bash
   cp .env.example .env
   ```
3. Start the app:
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000`.

## Deploy to Azure App Service

### 1) Create Azure resources

```bash
az login
az group create --name rg-weather-dashboard --location eastus
az appservice plan create --name plan-weather-dashboard --resource-group rg-weather-dashboard --sku B1 --is-linux
az webapp create --resource-group rg-weather-dashboard --plan plan-weather-dashboard --name <your-unique-app-name> --runtime "PYTHON|3.11"
```

### 2) Configure required app settings

Set application settings in Azure (replace placeholders):

```bash
az webapp config appsettings set \
  --resource-group rg-weather-dashboard \
  --name <your-unique-app-name> \
  --settings OWM_API_KEY=<your_openweathermap_api_key> FLASK_DEBUG=false REQUEST_TIMEOUT=10
```

### 3) Configure startup command

```bash
az webapp config set \
  --resource-group rg-weather-dashboard \
  --name <your-unique-app-name> \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

### 4) Deploy code

From the repository root:

```bash
az webapp up --resource-group rg-weather-dashboard --name <your-unique-app-name> --runtime "PYTHON|3.11"
```

### 5) Open the app

```bash
az webapp browse --resource-group rg-weather-dashboard --name <your-unique-app-name>
```

Your app will be available at `https://<your-unique-app-name>.azurewebsites.net`.
