import unittest
from trip import Trip

class TestTrip(unittest.TestCase):

    def test_trip_initialization(self):
        trip = Trip(trip_id=1, origin=10, destination=20, start=5, route=[1, 2, 3])
        self.assertEqual(trip.trip_id, 1)
        self.assertEqual(trip.origin, 10)
        self.assertEqual(trip.destination, 20)
        self.assertEqual(trip.start, 5)
        self.assertEqual(trip.route, [1, 2, 3])
        self.assertIsNone(trip.end)
        self.assertEqual(trip.travel_times, [])

    def test_trip_default_initialization(self):
        trip = Trip()
        self.assertEqual(trip.trip_id, 0)
        self.assertEqual(trip.origin, 0)
        self.assertEqual(trip.destination, 0)
        self.assertEqual(trip.start, 0)
        self.assertEqual(trip.route, [])
        self.assertIsNone(trip.end)
        self.assertEqual(trip.travel_times, [])

    def test_trip_from_continuous_demand(self):
        demand_pattern = [1, 2, 3]
        trips = Trip.from_continuous_demand(demand_pattern, total_time=6)
        self.assertEqual(len(trips), 12)       
        self.assertAlmostEqual(trips[1].start,1.0)
        self.assertAlmostEqual(trips[6].start,4.0)
    
    def test_trip_with_route_split(self):
        demand_pattern = [1, 2, 3]
        route_integer_share = {1: 1, 2: 2}
        trips = Trip.from_continuous_demand(demand_pattern, total_time=6, route_integer_share=route_integer_share)
        self.assertEqual(len(trips), 12)
        expected_routes = [1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2]
        for i, trip in enumerate(trips):
            self.assertEqual(trip.route, expected_routes[i])





if __name__ == '__main__':
    unittest.main()