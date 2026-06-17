/**
 * app.js — Weather Dashboard browser-side logic
 *
 * Responsibilities:
 *  - Submit city search to the Flask backend (/api/weather)
 *  - Render normalized weather JSON into the dashboard
 *  - Handle C/F unit toggle (client-side conversion, no re-fetch)
 *  - Manage loading, empty, and error UI states
 *  - Debounce rapid form submissions
 */

(() => {
  'use strict';

  // ── DOM refs ────────────────────────────────────────────────
  const form          = document.getElementById('search-form');
  const cityInput     = document.getElementById('city-input');
  const searchBtn     = document.getElementById('search-btn');
  const searchError   = document.getElementById('search-error');

  const loadingState  = document.getElementById('loading-state');
  const errorState    = document.getElementById('error-state');
  const errorMessage  = document.getElementById('error-message');
  const retryBtn      = document.getElementById('retry-btn');

  const resultsSection    = document.getElementById('results-section');
  const resultCity        = document.getElementById('result-city');
  const resultCountry     = document.getElementById('result-country');
  const resultCondition   = document.getElementById('result-condition');
  const resultTemp        = document.getElementById('result-temp');
  const resultFeelsLike   = document.getElementById('result-feels-like');
  const resultHumidity    = document.getElementById('result-humidity');
  const resultWind        = document.getElementById('result-wind');
  const resultVisibility  = document.getElementById('result-visibility');
  const resultTimestamp   = document.getElementById('result-timestamp');

  const unitBtns      = document.querySelectorAll('.unit-btn');

  // ── State ────────────────────────────────────────────────────
  let currentUnit     = 'C';        // 'C' | 'F'
  let lastData        = null;        // last successful normalized response
  let debounceTimer   = null;

  // ── Helpers ──────────────────────────────────────────────────
  function celsiusToFahrenheit(c) {
    return (c * 9) / 5 + 32;
  }

  function convertTemp(tempC, unit) {
    if (unit === 'F') return Math.round(celsiusToFahrenheit(tempC));
    return Math.round(tempC);
  }

  function formatTemp(tempC, unit) {
    return `${convertTemp(tempC, unit)}°${unit}`;
  }

  function formatWindSpeed(mps, unit) {
    // OWM returns m/s; convert to mph for Fahrenheit (imperial) users
    if (unit === 'F') return `${Math.round(mps * 2.237)} mph`;
    return `${Math.round(mps)} m/s`;
  }

  function formatVisibility(metres) {
    if (metres >= 1000) return `${(metres / 1000).toFixed(1)} km`;
    return `${metres} m`;
  }

  function formatTimestamp(isoString) {
    if (!isoString) return '';
    const d = new Date(isoString);
    return `Updated ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  }

  // ── UI state helpers ─────────────────────────────────────────
  function showOnly(stateId) {
    [loadingState, errorState, resultsSection].forEach(el => {
      el.hidden = el.id !== stateId;
    });
  }

  function hideAll() {
    loadingState.hidden  = true;
    errorState.hidden    = true;
    resultsSection.hidden = true;
  }

  function setSearchError(msg) {
    searchError.textContent = msg;
    searchError.hidden = !msg;
    cityInput.classList.toggle('invalid', !!msg);
  }

  function setLoading(active) {
    searchBtn.disabled = active;
    if (active) {
      showOnly('loading-state');
    }
  }

  // ── Render weather data ───────────────────────────────────────
  function renderWeather(data, unit) {
    resultCity.textContent      = data.city;
    resultCountry.textContent   = data.country ? `(${data.country})` : '';
    resultCondition.textContent = data.condition;
    resultTemp.textContent      = formatTemp(data.temp_c, unit);
    resultFeelsLike.textContent = formatTemp(data.feels_like_c, unit);
    resultHumidity.textContent  = `${data.humidity}%`;
    resultWind.textContent      = formatWindSpeed(data.wind_speed_mps, unit);
    resultVisibility.textContent = formatVisibility(data.visibility_m);
    resultTimestamp.textContent = formatTimestamp(data.timestamp);
    showOnly('results-section');
  }

  // ── Fetch from Flask backend ──────────────────────────────────
  async function fetchWeather(city) {
    const params = new URLSearchParams({ city: city.trim() });
    const response = await fetch(`/api/weather?${params}`, {
      headers: { 'Accept': 'application/json' }
    });

    const json = await response.json();

    if (!response.ok) {
      // Use error message from the backend if available
      const msg = json?.error || `Unexpected error (${response.status})`;
      throw new Error(msg);
    }

    return json;
  }

  // ── Form submit handler ───────────────────────────────────────
  async function handleSearch(event) {
    if (event) event.preventDefault();

    // Debounce: cancel any pending submit within 300ms
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {

      const city = cityInput.value.trim();
      setSearchError('');

      if (!city) {
        setSearchError('Please enter a city name.');
        cityInput.focus();
        return;
      }

      setLoading(true);

      try {
        const data = await fetchWeather(city);
        lastData = data;
        renderWeather(data, currentUnit);
      } catch (err) {
        errorMessage.textContent = err.message || 'Something went wrong. Please try again.';
        showOnly('error-state');
        lastData = null;
      } finally {
        setLoading(false);
      }

    }, 300);
  }

  // ── Unit toggle ───────────────────────────────────────────────
  function handleUnitToggle(event) {
    const btn = event.currentTarget;
    const unit = btn.dataset.unit;
    if (unit === currentUnit) return;

    currentUnit = unit;

    unitBtns.forEach(b => {
      const isActive = b.dataset.unit === unit;
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-pressed', String(isActive));
    });

    // Re-render with the new unit if data is available (no network call)
    if (lastData) {
      renderWeather(lastData, currentUnit);
    }
  }

  // ── Retry button ──────────────────────────────────────────────
  function handleRetry() {
    hideAll();
    handleSearch(null);
  }

  // ── Event listeners ───────────────────────────────────────────
  form.addEventListener('submit', handleSearch);
  retryBtn.addEventListener('click', handleRetry);
  unitBtns.forEach(btn => btn.addEventListener('click', handleUnitToggle));

  // Clear inline validation on input
  cityInput.addEventListener('input', () => setSearchError(''));

})();
