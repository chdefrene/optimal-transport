import json
import unittest
from unittest.mock import patch

from business_logic.route_planner import parse_route_instructions, calculate_route

with open('mocks/calculate_route.json') as file:
    mock_route_data = json.load(file)


class CalculateRouteTestCase(unittest.TestCase):
    @patch('requests.get')
    def test_calculate_route_ok(self, mock):
        mock.return_value.status_code = 200
        mock.return_value.json.return_value = mock_route_data

        destination = {"latitude": 69.78432418819496, "longitude": 29.947542386712723}
        data = calculate_route(destination)

        self.assertEqual(len(data), 131)
        mock.assert_called_once()

    @patch('requests.get')
    def test_calculate_route_failure(self, mock):
        mock.return_value.status_code = 400

        destination = {"latitude": None, "longitude": None}
        data = calculate_route(destination)

        self.assertEqual(data, [])
        mock.assert_called_once()


class ParseRouteInstructionsTestCase(unittest.TestCase):
    def setUp(self):
        self.instructions = mock_route_data['routes'][0]['guidance']['instructions']

    # Total distance 4.2 km => 1 split
    def test_parse_route_instructions_short(self):
        result = parse_route_instructions(self.instructions[:10])

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            {"point": {"latitude": 59.91912, "longitude": 10.73542}, "hours_offset": 0}
        )

    # Total distance 188 km => 7 splits
    def test_parse_route_instructions_medium(self):
        result = parse_route_instructions(self.instructions[:25])

        self.assertEqual(len(result), 7)

    # Total distance 2057 km => 69 splits,
    # (some instructions have a distance greater than 30 km)
    def test_parse_route_instructions_long(self):
        result = parse_route_instructions(self.instructions)

        self.assertEqual(len(result), 64)


if __name__ == '__main__':
    unittest.main()
