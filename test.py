import json
import unittest
from unittest.mock import patch, MagicMock

from business_logic.route_planner import parse_route_instructions, calculate_route
from business_logic.weather import get_weather_report, calculate_weather_delay

with open('mocks/calculate_route.json') as file:
    mock_route_data = json.load(file)

with open('mocks/current_weather_and_forecast.json') as file:
    mock_weather_data = json.load(file)


class CalculateRouteTestCase(unittest.TestCase):
    @patch('requests.get')
    def test_calculate_route_ok(self, mock):
        mock.return_value.status_code = 200
        mock.return_value.json.return_value = mock_route_data

        destination = {"latitude": 69.78432418819496, "longitude": 29.947542386712723}
        data = calculate_route(destination)

        self.assertEqual(data['summary']['travelTimeInSeconds'], 81997)
        self.assertEqual(len(data['guidance']['instructions']), 131)
        mock.assert_called_once()

    @patch('requests.get')
    def test_calculate_route_failure(self, mock):
        mock.return_value.status_code = 400

        destination = {"latitude": None, "longitude": None}
        data = calculate_route(destination)

        # self.assertEqual(data, {})
        mock.assert_called_once()


class ParseRouteInstructionsTestCase(unittest.TestCase):
    instructions = mock_route_data['routes'][0]['guidance']['instructions']

    # Total distance 4.2 km => 1 split
    def test_parse_route_instructions_short(self):
        result = parse_route_instructions(self.instructions[:10])

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[-1],
            {
                "point": {"latitude": 59.91912, "longitude": 10.73542},
                "hours_offset": 0,
                "travel_time": 0
            }
        )

    # Total distance 188 km => 7 splits
    def test_parse_route_instructions_medium(self):
        result = parse_route_instructions(self.instructions[:25])

        self.assertEqual(len(result), 7)
        self.assertEqual(
            result[-1],
            {
                "point": {'latitude': 59.30051, 'longitude': 13.07207},
                "hours_offset": 2,
                "travel_time": 5245
            }
        )

    # Total distance 2057 km => 69 splits,
    # (some instructions have a distance greater than 30 km, which explains the fewer splits)
    def test_parse_route_instructions_long(self):
        result = parse_route_instructions(self.instructions)

        self.assertEqual(len(result), 64)
        self.assertEqual(
            result[-1],
            {
                "point": {'latitude': 69.74325, 'longitude': 29.90249},
                "hours_offset": 22,
                "travel_time": 45303
            }
        )


class GetWeatherReportTestCase(unittest.TestCase):
    @patch('requests.get')
    def test_get_weather_report_ok(self, mock):
        mock.return_value.status_code = 200
        mock.return_value.json.return_value = mock_weather_data

        location = {"latitude": 69.78432418819496, "longitude": 29.947542386712723}
        data = get_weather_report(location)

        self.assertEqual(data['current']['weather'][0]['main'], 'Clear')
        self.assertEqual(data['hourly'][-1]['weather'][0]['main'], 'Clouds')
        mock.assert_called_once()

    @patch('requests.get')
    def test_get__weather_report_failure(self, mock):
        mock.return_value.status_code = 400

        destination = {"latitude": None, "longitude": None}
        data = get_weather_report(destination)

        self.assertEqual(data, {})
        mock.assert_called_once()


class CalculateWeatherDelayTestCase(unittest.TestCase):
    geo_point = {
        "point": {'latitude': 69.74325, 'longitude': 29.90249},
        "hours_offset": 0,
        "travel_time": 45303
    }
    weather_report = {
        "current": {
            "weather": [
                {
                    "id": 800,
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01n"
                }
            ]
        },
        "hourly": [
            {
                "weather": [
                    {
                        "id": 503,
                        "main": "Rain",
                        "description": "very heavy rain",
                        "icon": "10d"
                    }
                ],
            },
            {
                "weather": [
                    {
                        "id": 602,
                        "main": "Snow",
                        "description": "heavy snow",
                        "icon": "13d"
                    }
                ],
            },
        ]
    }

    def test_calculate_weather_delay_current(self):
        result = calculate_weather_delay(self.geo_point, self.weather_report)

        self.assertEqual(result, 0)

    # Rain => 5% increase
    def test_calculate_weather_delay_forecast_1(self):
        geo_point = self.geo_point
        geo_point['hours_offset'] = 1

        result = calculate_weather_delay(geo_point, self.weather_report)

        self.assertEqual(result,  2265.15)

    # Snow => 10% increase
    def test_calculate_weather_delay_forecast_2(self):
        geo_point = self.geo_point
        geo_point['hours_offset'] = 2

        result = calculate_weather_delay(geo_point, self.weather_report)

        self.assertEqual(result, 4530.3)


if __name__ == '__main__':
    unittest.main()
