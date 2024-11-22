import unittest
from unittest.mock import Mock
from discrete.originNode import OriginNode

from discrete.link import Link  # Adjust the import based on the actual module structure
import trip

class TestOriginNode(unittest.TestCase):

    def setUp(self):
        # Initialize a Link object and an OriginNode object before each test
        self.link = Mock(spec=Link)
        self.link.get_supply.return_value = 0.5
        self.demands = trip.Trip.from_continuous_demand([0.5], 120, route=[1,])
        self.origin_node = OriginNode(node_id=1, link=self.link, demand_trips=self.demands)
        self.origin_node.start(time_step=1, total_time=120)

    def test_initial_state(self):
        # Test the initial state of the OriginNode object
        self.assertIsNotNone(self.origin_node)
        self.assertEqual(self.origin_node.node_id, 1)
        self.assertEqual(self.origin_node.total_time, 120)
        self.assertEqual(self.origin_node.time_step, 1)
        self.assertEqual(self.origin_node.total_steps, 120)

        self.link.get_supply.return_value = 0
        self.origin_node.prepare_step(0)
        self.assertEqual(self.origin_node._demand, 1.0)
        self.origin_node.compute_flows(0)
        self.assertEqual(self.link.set_inflow.call_count, 1)
        self.assertEqual(self.link.set_inflow.call_args[0][0], [])

        self.link.get_supply.return_value = 1.0
        self.origin_node.prepare_step(1)
        self.origin_node.compute_flows(1)
        self.assertEqual(self.link.set_inflow.call_count, 2)

        #vehicle left the queue and entered the link.
        inflow = self.link.set_inflow.call_args[0][0]
        self.assertEqual(len(inflow), 1)
        self.assertNotIn(inflow[0], self.origin_node.entry_queue)




    def tearDown(self):
        # Clean up after each test
        del self.origin_node
        del self.link

if __name__ == '__main__':
    unittest.main()