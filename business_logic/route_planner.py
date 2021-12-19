import math
import os

import requests

OPTIMAL_TRANSPORT = {
    'address': 'Edvard Storms gate 2',
    'postcode': '0166',
    'city': 'Oslo',
    'latitude': '59.91909213270675',
    'longitude': '10.735432996844944',
}


def calculate_route(destination):
    """
    Use TomTom API to plan a route from Optimal Transport HQ
    to the provided destination.
    """
    ot_lat, ot_lng = OPTIMAL_TRANSPORT['latitude'], OPTIMAL_TRANSPORT['longitude']
    locations = f"{ot_lat},{ot_lng}:{destination.get('latitude')},{destination.get('longitude')}"

    payload = {
        "key": os.environ.get('TOMTOM_API_KEY'),
        "instructionsType": "coded",
        "routeRepresentation": "summaryOnly",
        # "departAt": "2021-12-31T15:06:27+01:00",
        "vehicleCommercial": True,
    }

    response = requests.get(f"https://api.tomtom.com/routing/1/calculateRoute/{locations}/json", params=payload)

    if response.status_code == 200:
        return response.json().get('routes', [{}])[0]

    return {}


def parse_route_instructions(instructions):
    """
    Traverse the route instructions, dividing it up into 30 km intervals.
    This will be used later on when fetching weather data.
    """
    geo_points = []

    distance_counter = 0
    for i, instruction in enumerate(instructions):
        if i == 0 or instruction['routeOffsetInMeters'] >= distance_counter:
            # Ensures we can lookup weather data at the
            # point in time when we reach this geo point
            hours_offset = math.floor(instruction['travelTimeInSeconds'] / 3600)

            data = {"point": instruction['point'], "hours_offset": hours_offset}
            geo_points.append(data)

            # Re-fetch weather data after 30km
            distance_counter += 30000

    return geo_points
