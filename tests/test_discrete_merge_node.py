import unittest
from unittest.mock import Mock
from discrete.mergeNode import MergeNode
from discrete.link import Link 

class TestMergeNode(unittest.TestCase):

    def setUp(self):
        pass
    def test_initial_state(self):
        # Test the initial state of the OneToOneNode object

        outbound_link = Mock(spec=Link)
        inbound_links = []
        for i in range(2):
            inbound_links.append(Mock(spec=Link))
        
        merge_node = MergeNode(1, outbound_link, inbound_links, [0,1])
        merge_node.start(time_step=1, total_time=3600)

        self.assertIsNotNone(merge_node)
        self.assertEqual(merge_node.node_id, 1)
        self.assertEqual(merge_node.total_time, 3600)
        self.assertEqual(merge_node.time_step, 1)
        self.assertEqual(merge_node.total_steps, 3600)


    def test_compute_flows(self):
        # Test the compute_flows method

        outbound_link = Mock(spec=Link)
        inbound_links = []
        for i in range(2):
            inbound_links.append(Mock(spec=Link))
        
        merge_node = MergeNode(1, outbound_link, inbound_links, [0,1])
        merge_node.start(time_step=1, total_time=3600)

        
        inbound_links[0].get_demand.return_value = 0
        inbound_links[0].get_cumulative_demand_term.return_value = 0
        inbound_links[1].get_demand.return_value = 1
        outbound_link.get_supply.return_value = 1

        inbound_links[1].set_outflow.return_value = ['vehicle1']
        inbound_links[1].get_vehicle_from_index.return_value = 'vehicle1'

        merge_node.prepare_step(0)

        merge_node.compute_flows(0)

        inbound_links[0].set_outflow.assert_called_once_with(0)
        inbound_links[1].set_outflow.assert_called_once_with(1)
        outbound_link.set_inflow.assert_called_once_with(['vehicle1'])


if __name__ == '__main__':
    unittest.main()