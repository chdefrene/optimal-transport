import os

import requests


def get_current_weather(location):
    payload = {
        "appid": os.environ.get('OPEN_WEATHER_API_KEY'),
        "lat": location.get('latitude'),
        "lon": location.get('longitude'),
        "units": "metric"
    }

    response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=payload)

    if response.status_code == 200:
        return response.json().get('weather', [])

    return []
