import unittest
from unittest.mock import Mock
from continuousSingleCommodity.destinationNode import DestinationNode
from continuousSingleCommodity.link import Link


class TestDestinationNode(unittest.TestCase):

    def setUp(self):
        # Initialize a Link object and a DestinationNode object before each test
        self.link = Mock(spec=Link)
        self.link.get_demand.return_value = 0.5
        self.destination_node = DestinationNode(node_id=1, link=self.link)
        self.destination_node.start(time_step=1, total_time=3600)

    def test_initial_state(self):
        # Test the initial state of the DestinationNode object
        self.assertIsNotNone(self.destination_node)
        self.assertEqual(self.destination_node.node_id, 1)
        self.assertEqual(self.destination_node.total_time, 3600)
        self.assertEqual(self.destination_node.time_step, 1)
        self.assertEqual(self.destination_node.total_steps, 3600)
        self.assertEqual(len(self.destination_node.inflow), 3600)

    def test_prepare_step(self):
        # Test the prepare_step method
        self.destination_node.prepare_step(0)
        # Add assertions if prepare_step modifies any state

    def test_compute_flows(self):
        # Test the compute_flows method
        self.destination_node.compute_flows(0)
        self.assertEqual(self.link.set_outflow.call_count, 1)
        self.assertEqual(self.link.set_outflow.call_args[0][0], 0.5)
        self.assertEqual(self.destination_node.inflow[0], 0.5)


if __name__ == "__main__":
    unittest.main()
