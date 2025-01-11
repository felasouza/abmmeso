import unittest
from unittest.mock import Mock
from discrete.destinationNode import DestinationNode
from discrete.link import Link
from demand.trip import Trip


class TestDestinationNode(unittest.TestCase):

    def setUp(self):
        # Initialize a Link object and a DestinationNode object before each test
        self.link = Mock(spec=Link)

        self.destination_node = DestinationNode(node_id=1, link=self.link)
        self.destination_node.start(time_step=1, total_time=120)

    def test_initial_state(self):
        # Test the initial state of the DestinationNode object
        self.assertIsNotNone(self.destination_node)
        self.assertEqual(self.destination_node.node_id, 1)
        self.assertEqual(self.destination_node.total_time, 120)
        self.assertEqual(self.destination_node.time_step, 1)
        self.assertEqual(self.destination_node.total_steps, 120)
        self.assertEqual(len(self.destination_node.inflow), 120)

    def test_prepare_step(self):
        # Test the prepare_step method
        self.destination_node.prepare_step(0)
        # Add assertions if prepare_step modifies any state

    def test_compute_flows(self):
        # Test the compute_flows method
        vehicle_1 = Trip(
            trip_id=1,
            origin=3,
            destination=4,
            start=0,
            route=[
                1,
            ],
        )
        self.link.get_demand.return_value = 1
        self.link.set_outflow.return_value = [
            vehicle_1,
        ]
        self.destination_node.compute_flows(0)
        self.assertEqual(self.link.set_outflow.call_count, 1)
        self.assertEqual(self.link.set_outflow.call_args[0][0], 1)
        self.assertEqual(self.destination_node.arrived_vehicles, [vehicle_1])
        self.assertIsNotNone(vehicle_1.end)
        arrived_trips = self.destination_node.get_arrived_trips()
        self.assertDictEqual(
            arrived_trips[0],
            {
                "trip_id": 1,
                "origin": 3,
                "destination": 4,
                "start": 0,
                "end": vehicle_1.end,
            },
        )


if __name__ == "__main__":
    unittest.main()
