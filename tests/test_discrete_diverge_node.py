import unittest
from unittest.mock import Mock
from discrete.divergeNode import DivergeNode
from discrete.link import Link 

class TestOneToOneNode(unittest.TestCase):

    def setUp(self):
        pass
    def test_initial_state(self):
        # Test the initial state of the OneToOneNode object

        inbound_link = Mock(spec=Link)
        outbound_links = []
        for i in range(2):
            outbound_links.append(Mock(spec=Link))
        
        diverge_node = DivergeNode(node_id=1, inbound_link=inbound_link, outbound_links=outbound_links)
        diverge_node.start(time_step=1, total_time=3600)

        self.assertIsNotNone(diverge_node)
        self.assertEqual(diverge_node.node_id, 1)
        self.assertEqual(diverge_node.total_time, 3600)
        self.assertEqual(diverge_node.time_step, 1)
        self.assertEqual(diverge_node.total_steps, 3600)

    def test_compute_flows(self):
        # Test the compute_flows method

        inbound_link = Mock(spec=Link)
        inbound_link.get_vehicle_from_index.return_value = 'vehicle1'
        inbound_link.set_outflow.return_value = ['vehicle1']
        outbound_links = []
        for i in range(2):
            outbound_links.append(Mock(spec=Link))
        
        diverge_node = DivergeNode(node_id=1, inbound_link=inbound_link, outbound_links=outbound_links)
        diverge_node.start(time_step=1, total_time=3600)
        diverge_node.get_outbound_vehicle_from_vehicle = Mock()
        diverge_node.get_outbound_vehicle_from_vehicle.side_effect = [0,1]

        inbound_link.get_demand.return_value = 2
        outbound_links[0].get_supply.return_value = 1
        outbound_links[1].get_supply.return_value = 0

        diverge_node.compute_flows(0)
        inbound_link.set_outflow.assert_called_once_with(1)
        outbound_links[0].set_inflow.assert_called_once_with(['vehicle1'])
        outbound_links[1].set_inflow.assert_called_once_with([])


        


if __name__ == '__main__':
    unittest.main()