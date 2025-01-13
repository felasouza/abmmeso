import unittest
from unittest.mock import Mock
from continuousSingleCommodity.mergeNode import MergeNode
from continuousSingleCommodity.link import Link

class TestMergeNode(unittest.TestCase):

    def setUp(self):
        self.outbound_link = Mock(spec=Link)
        self.inbound_links = []
        for i in range(2):
            self.inbound_links.append(Mock(spec=Link))
            self.inbound_links[i].cap = 0.5
        self.outbound_link.get_supply.return_value = 0.5
        self.node = MergeNode(node_id=1, outbound_link=self.outbound_link, inbound_links=self.inbound_links, priorities=[0.5, 0.5])

        self.node.start(time_step=1, total_time=3600)

    def test_initial_state(self):
        self.assertIsNotNone(self.node)
        self.assertEqual(self.node.node_id, 1)
        self.assertEqual(self.node.total_time, 3600)
        self.assertEqual(self.node.time_step, 1)
        self.assertEqual(self.node.total_steps, 3600)


    def test_compute_flows(self):
        # Test the compute_flows method
        self.inbound_links[0].get_demand.return_value = 0.3
        self.inbound_links[1].get_demand.return_value = 0.3
        self.node.compute_flows(0)
        self.assertEqual(self.outbound_link.get_supply.call_count, 1)
        for inbound_link in self.inbound_links:
            self.assertEqual(inbound_link.get_demand.call_count, 1)

        self.outbound_link.set_inflow.assert_called_once_with(0.5)
        self.inbound_links[0].set_outflow.assert_called_once_with(0.25)
        self.inbound_links[1].set_outflow.assert_called_once_with(0.25)
        
    def test_three_inbound_links(self):

        capacities = [0.5, 0.25, 0.5]
        demands = [0.3, 0.2, 0.3]
        
        expected_flows = [0.2, 0.1, 0.2]
        self.assert_for_case(capacities, demands, expected_flows)
        
        demands = [0.1, 0.1, 0.3]
        expected_flows = [0.1, 0.1, 0.3]
        self.assert_for_case(capacities, demands, expected_flows)
        
        demands = [0.0, 0.0, 0]
        expected_flows = [0.0, 0.0, 0.0]
        self.assert_for_case(capacities, demands, expected_flows)

    def assert_for_case(self, capacities, demands, expected_flows):
        outbound_link = Mock(spec=Link)
        inbound_links = []
        for i in range(3):
            inbound_links.append(Mock(spec=Link))
            inbound_links[i].get_capacity.return_value = capacities[i]
            inbound_links[i].get_demand.return_value = demands[i]
        outbound_link.get_supply.return_value = 0.5
        node = MergeNode(node_id=1, outbound_link=outbound_link, inbound_links=inbound_links)
        node.start(time_step=1, total_time=10)
        
        node.compute_flows(0)
        self.assertEqual(outbound_link.get_supply.call_count, 1)
        for inbound_link in inbound_links:
            self.assertEqual(inbound_link.get_demand.call_count, 1)
            
        for i in range(3):
            self.assertAlmostEqual(inbound_links[i].set_outflow.call_args[0][0], expected_flows[i])
        self.assertAlmostEqual(outbound_link.set_inflow.call_args[0][0], sum(expected_flows))
        



if __name__ == '__main__':
    unittest.main()