import unittest
from unittest.mock import Mock
from continuousSingleCommodity.divergeNode import DivergeNode
from continuousSingleCommodity.link import Link

class TestDivergeNode(unittest.TestCase):

    def setUp(self):
        self.inbound_link = Mock(spec=Link)
        self.outbound_links = []
        for i in range(2):
            self.outbound_links.append(Mock(spec=Link))
        self.inbound_link.get_demand.return_value = 0.5
        self.node = DivergeNode(node_id=1, inbound_link=self.inbound_link, outbound_links=self.outbound_links,
                                           turn_rates=[0.3, 0.7])
        self.node.start(time_step=1, total_time=3600)

    def test_initial_state(self):
        self.assertIsNotNone(self.node)
        self.assertEqual(self.node.node_id, 1)
        self.assertEqual(self.node.total_time, 3600)
        self.assertEqual(self.node.time_step, 1)
        self.assertEqual(self.node.total_steps, 3600)

    def test_prepare_step(self):
        # Test the prepare_step method
        self.node.prepare_step(0)

    def test_compute_flows(self):
        # Test the compute_flows method
        self.outbound_links[0].get_supply.return_value = 0.3
        self.outbound_links[1].get_supply.return_value = 0.3
        self.node.compute_flows(0)
        self.assertEqual(self.inbound_link.get_demand.call_count, 1)
        for outbound_link in self.outbound_links:
            self.assertEqual(outbound_link.get_supply.call_count, 1)

        self.inbound_link.set_outflow.assert_called_once_with(0.3/0.7)
        self.outbound_links[0].set_inflow.assert_called_once_with(0.3*0.3/0.7)
        self.outbound_links[1].set_inflow.assert_called_once_with(0.3)



if __name__ == '__main__':
    unittest.main()