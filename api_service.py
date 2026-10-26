
import requests
import pandas as pd

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"


def search_city(city_name):
    """Find a city and return its location details."""
    params = {
        "name": city_name,
        "count": 5,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=20
    )
    response.raise_for_status()
    data = response.json()

    return data.get("results", [])


def fetch_air_quality(latitude, longitude, past_days=7, forecast_days=3):
    """Fetch hourly air-quality data for a location."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "european_aqi,pm2_5,pm10,"
            "nitrogen_dioxide,ozone,carbon_monoxide"
        ),
        "past_days": past_days,
        "forecast_days": forecast_days,
        "timezone": "auto"
    }

    response = requests.get(
        AIR_QUALITY_URL,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    hourly = data.get("hourly", {})

    if not hourly or "time" not in hourly:
        raise ValueError("No air-quality data was returned for this location.")

    frame = pd.DataFrame(hourly)
    frame = frame.rename(columns={"time": "timestamp"})

    return frame
