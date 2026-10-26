
import numpy as np


def safe_float(value):
    """Convert a value to a number safely."""
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def aqi_category(aqi):
    """Return a category for the European Air Quality Index."""
    if aqi is None:
        return "Unknown"
    if aqi <= 20:
        return "Good"
    elif aqi <= 40:
        return "Fair"
    elif aqi <= 60:
        return "Moderate"
    elif aqi <= 80:
        return "Poor"
    elif aqi <= 100:
        return "Very Poor"
    return "Extremely Poor"


def health_advice(category):
    """Provide basic advice based on air quality."""
    advice = {
        "Good": "Enjoy outdoor activities as usual.",
        "Fair": "Air quality is generally acceptable.",
        "Moderate": "Sensitive people should consider reducing prolonged outdoor exertion.",
        "Poor": "Consider reducing prolonged outdoor activities.",
        "Very Poor": "Avoid prolonged outdoor exertion where possible.",
        "Extremely Poor": "Limit outdoor exposure and follow local health guidance.",
        "Unknown": "Air-quality information is unavailable."
    }
    return advice.get(category, advice["Unknown"])


def calculate_statistics(values):
    """Calculate basic statistics for numeric values."""
    numbers = np.array(
        [value for value in values if value is not None],
        dtype=float
    )

    if numbers.size == 0:
        return None, None, None

    return (
        float(np.mean(numbers)),
        float(np.min(numbers)),
        float(np.max(numbers))
    )
