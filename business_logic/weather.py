import os

import requests

# From the case description:
#  * Frost increases travel time by 10%
#  * Rain increases travel time by 5%
#
# Remaining values have been estimated.
# Unlikely conditions have been excluded.
WEATHER_CONDITION_DELAYS_MAP = {
    # "Ash": 0,
    # "Dust": 0,
    "Fog": 0.02,
    "Haze": 0.02,
    "Sand": 0.02,
    "Smoke": 0.02,
    "Squall": 0.1,
    # "Tornado": 0,
    "Clear": 0,
    "Clouds": 0,
    "Drizzle": 0.05,
    "Mist": 0.02,
    "Rain": 0.05,
    "Snow": 0.1,
    "Thunderstorm": 0.05,
}


def get_weather_report(location):
    """
    Use the OpenWeather API to get the current weather
    at the provided location
    """
    payload = {
        "appid": os.environ.get('OPEN_WEATHER_API_KEY'),
        "lat": location.get('latitude'),
        "lon": location.get('longitude'),
        "units": "metric",
        "exclude": "minutely,daily,alerts"
    }

    response = requests.get("https://api.openweathermap.org/data/2.5/onecall", params=payload)

    if response.status_code == 200:
        return response.json()

    return {}


def apply_weather_delay():
    pass
