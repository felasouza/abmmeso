import unittest
from unittest.mock import Mock
from continuousSingleCommodity.originNode import OriginNode

from continuousSingleCommodity.link import Link 

class TestOriginNode(unittest.TestCase):

    def setUp(self):
        # Initialize a Link object and an OriginNode object before each test
        self.link = Mock(spec=Link)
        self.link.get_supply.return_value = 0.5
        self.demands = [0.2, 0.6, 0.2]
        self.origin_node = OriginNode(node_id=1, link=self.link, demands=self.demands)
        self.origin_node.start(time_step=1, total_time=3600)

    def test_initial_state(self):
        # Test the initial state of the OriginNode object
        self.assertIsNotNone(self.origin_node)
        self.assertEqual(self.origin_node.node_id, 1)
        self.assertEqual(self.origin_node.demands, self.demands)
        self.assertEqual(self.origin_node.total_time, 3600)
        self.assertEqual(self.origin_node.time_step, 1)
        self.assertEqual(self.origin_node.total_steps, 3600)
        self.assertEqual(len(self.origin_node.demands_at_steps), 3600)
        self.assertEqual(len(self.origin_node.entry_queue), 3601)
        self.assertEqual(len(self.origin_node.outflow), 3600)
        self.assertEqual(self.origin_node.demands_at_steps[1199], 0.2)
        self.assertEqual(self.origin_node.demands_at_steps[1200], 0.6)


    def test_two_iterations(self):
        # Test the prepare_step method
        self.origin_node.prepare_step(0)
        self.assertEqual(self.origin_node._demand, 0.2)

        self.origin_node.compute_flows(0)
        self.assertEqual(self.link.set_inflow.call_count, 1)
        self.assertEqual(self.link.set_inflow.call_args[0][0], 0.2)
        self.assertEqual(self.origin_node.entry_queue[1], 0)
        self.assertEqual(self.origin_node.outflow[0], 0.2)
        self.origin_node.prepare_step(1)
        self.assertAlmostEqual(self.origin_node._demand, 0.2)
    
    def test_different_ratios(self):
        link = Mock(spec=Link)
        link.get_supply.return_value = 0.5
        demands = [0.2, 0.6, 0.2]
        origin_node = OriginNode(node_id=1, link=link, demands=demands)
        origin_node.start(time_step=3, total_time=3600)        




    def tearDown(self):
        # Clean up after each test
        del self.origin_node
        del self.link

if __name__ == '__main__':
    unittest.main()