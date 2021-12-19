from datetime import datetime, timedelta

from flask import Flask, Response
from flask import request
from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim

from business_logic.route_planner import calculate_route, parse_route_instructions, OPTIMAL_TRANSPORT
from business_logic.weather import get_weather_report, calculate_weather_delay

app = Flask(__name__)


def get_geo_location_from_address(search_term):
    geolocator = Nominatim(user_agent="Optimal Transport")
    location = geolocator.geocode(search_term)

    return {
        "latitude": location.latitude,
        "longitude": location.longitude,
    }


@app.route('/api/route', methods=['POST'])
def route():
    # Validate payload
    if not request.json.get("address"):
        return Response("No 'address' attribute provided!", status=400)

    try:
        geo_location = get_geo_location_from_address(request.json['address'])
    except GeocoderUnavailable:
        return Response("Could not look up the provided address. Please provide postcode and city.", status=400)

    optimal_route = calculate_route(geo_location)

    summary = optimal_route['summary']
    instructions = optimal_route['guidance']['instructions']

    geo_points = parse_route_instructions(instructions)

    total_delay = 0
    for geo_point in geo_points:
        weather_report = get_weather_report(geo_point['point'])

        # If there is only one split, the travel time will not have been set.
        # Use the original arrival time instead.
        if geo_point['travel_time'] == 0:
            geo_point['travel_time'] = summary['travelTimeInSeconds']

        delayed_travel_time = calculate_weather_delay(geo_point, weather_report)

        total_delay += delayed_travel_time

    now = datetime.now()
    total_travel_time = summary['travelTimeInSeconds'] + total_delay
    arrival = (now + timedelta(seconds=total_travel_time)).strftime(
        '%A, %d %B %Y at %H:%M:%S')

    return Response(
        f"<h1>Great success!</h1>"
        f"<p>Successfully calculated an optimal route from <b>{OPTIMAL_TRANSPORT['address']}</b> to <b>{request.json['address']}</b>.</p>"
        f"<p>The route is <b>{str(round(summary['lengthInMeters'] / 1000, 2)) + ' kilometers' if summary['lengthInMeters'] > 1000 else str(summary['lengthInMeters']) + ' meters'}</b>.</p>"
        f"<p>The original route was estimated to take <b>{summary['travelTimeInSeconds']} seconds</b> ({round(summary['travelTimeInSeconds'] / 3600, 2)} hours).</p>"
        f"<p>Local weather conditions will cause an additional delay of <b>{total_delay} seconds</b>.</p>"
        f"<p>If you leave now, you will arrive <b>{arrival}</b>.</p>",
        mimetype="text/html"
    )


if __name__ == "__main__":
    app.run()
