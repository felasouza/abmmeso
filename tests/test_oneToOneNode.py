# FILE: tests/test_oneToOneNode.py

import unittest
from unittest.mock import Mock
from continuous.oneToOneNode import OneToOneNode
from continuous.link import Link  # Adjust the import based on the actual module structure

class TestOneToOneNode(unittest.TestCase):

    def setUp(self):
        # Initialize Link objects and a OneToOneNode object before each test
        self.inbound_link = Mock(spec=Link)
        self.outbound_link = Mock(spec=Link)
        self.inbound_link.get_demand.return_value = 0.5
        self.outbound_link.get_supply.return_value = 0.3
        self.one_to_one_node = OneToOneNode(node_id=1, inbound_link=self.inbound_link, outbound_link=self.outbound_link)
        self.one_to_one_node.start(time_step=1, total_time=3600)

    def test_initial_state(self):
        # Test the initial state of the OneToOneNode object
        self.assertIsNotNone(self.one_to_one_node)
        self.assertEqual(self.one_to_one_node.node_id, 1)
        self.assertEqual(self.one_to_one_node.total_time, 3600)
        self.assertEqual(self.one_to_one_node.time_step, 1)
        self.assertEqual(self.one_to_one_node.total_steps, 3600)

    def test_prepare_step(self):
        # Test the prepare_step method
        self.one_to_one_node.prepare_step(0)
        # Add assertions if prepare_step modifies any state

    def test_compute_flows(self):
        # Test the compute_flows method
        self.one_to_one_node.compute_flows(0)
        self.assertEqual(self.inbound_link.get_demand.call_count, 1)
        self.assertEqual(self.inbound_link.get_supply.call_count,0)
        self.assertEqual(self.outbound_link.get_supply.call_count, 1)
        self.assertEqual(self.outbound_link.get_demand.call_count, 0)

        self.assertEqual(self.inbound_link.set_outflow.call_count, 1)
        self.assertEqual(self.inbound_link.set_outflow.call_args[0][0], 0.3)
        self.assertEqual(self.outbound_link.set_inflow.call_count, 1)
        self.assertEqual(self.outbound_link.set_inflow.call_args[0][0], 0.3)

if __name__ == '__main__':
    unittest.main()