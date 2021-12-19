import unittest

import json

from business_logic.route_planner import parse_route_instructions

with open('mocks/instructions.json') as file:
    instructions = json.load(file)


class ParseRouteInstructionsTestCase(unittest.TestCase):
    # Total distance 4.2 km => 1 split
    def test_parse_route_instructions_short(self):
        result = parse_route_instructions(instructions[:10])

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            {"point": {"latitude": 59.91912, "longitude": 10.73542}, "hours_offset": 0}
        )

    # Total distance 188 km => 7 splits
    def test_parse_route_instructions_medium(self):
        result = parse_route_instructions(instructions[:25])

        self.assertEqual(len(result), 7)

    # Total distance 2057 km => 69 splits,
    # (some instructions have a distance greater than 30 km)
    def test_parse_route_instructions_long(self):
        result = parse_route_instructions(instructions)

        self.assertEqual(len(result), 64)


if __name__ == '__main__':
    unittest.main()
