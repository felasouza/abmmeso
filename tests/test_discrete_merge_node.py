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


    def test_compute_flows_simple_case(self):
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

    def test_compute_flows_congested(self):
        cases = [
            {'total_steps': 4,
             'capacity': 0.5, 'demands': {0: [0,1,0,1], 1: [1,1,1,0]}, 'expected_flows': {0: [0,1,0,1], 1: [0,0,1,0]}, 
                'outbound_flows': [[], ['vehicle01'], ['vehicle12'], ['vehicle03']]},
        ]


        for case in cases:
            outbound_link = Mock(spec=Link)
            
            inbound_links = []
            for i in range(2):
                inbound_links.append(Mock(spec=Link))
            
            priority_minimum_size = max(len(inbound_links), int(case['capacity'] * 2))
            if priority_minimum_size % 2 == 1:
                priority_minimum_size += 1
            priority_vector = [i % 2 for i in range(priority_minimum_size)]

            merge_node = MergeNode(1, outbound_link, inbound_links, priority_vector)
            merge_node.start(time_step=1, total_time=3600)

            for inb in inbound_links:
                inb.get_cumulative_demand_term.return_value = 3
            
            demands = case['demands']
            expected_flows = case['expected_flows']
            expected_outbound_flows = case['outbound_flows']

            for t in range(case['total_steps']):
                outbound_link.get_supply.return_value = 1
            for i, inb in enumerate(inbound_links):
                inb.get_demand.return_value = demands[i][t]
                if expected_flows[i][t] > 0:
                    inb.set_outflow.return_value = [f'vehicle{i}{t}']
                    inb.get_vehicle_from_index.return_value = f'vehicle{i}{t}'
                print(i, t, f'vehicle{i}{t}')
            
            merge_node.prepare_step(t)
            merge_node.compute_flows(t)
            outbound_link.set_inflow.assert_called_once_with(expected_outbound_flows[t])
            for i, inb in enumerate(inbound_links):
                inb.set_outflow.assert_called_once_with(expected_flows[i][t])
            
            outbound_link.set_inflow.reset_mock()
            for inb in inbound_links:
                inb.set_outflow.reset_mock()
                




if __name__ == '__main__':
    unittest.main()