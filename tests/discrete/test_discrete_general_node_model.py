import unittest
from discrete.generalNodeModel import GeneralNodeModel
from discrete.link import Link
from unittest.mock import MagicMock


class TestGeneralNodeModel(unittest.TestCase):

    def setUp(self):
       pass

    def test_initialization(self):
        # Test if the object is initialized correctly

        node = self.create_node()

        self.assertIsInstance(node, GeneralNodeModel)
    
    def test_jumping_no_demand(self):
        case = {'demands': [1, 0, 1], 'supplies': [1, 1, 1], 'outbound_links': [0, 2],
                'expected_outflows': [1, 0, 1], 'expected_inflows': [1, 0, 1], 'start_priority': 0,
                'end_priority': 0}
        self.run_case(case)

    def test_stuck_in_demand(self):
        case = {'demands': [1, 1, 1], 'supplies': [1, 0, 1], 'outbound_links': [0, 1, 1],
                'expected_outflows': [1, 0, 0], 'expected_inflows': [1, 0, 0], 'start_priority': 0,
                'end_priority': 1}
        self.run_case(case)

    def test_forward_mechanism_with_no_change_in_priority(self):
        case = {'demands': [1, 1, 1], 'supplies': [1, 0, 1], 'outbound_links': [0, 1, 2],
                'expected_outflows': [1, 0, 1], 'expected_inflows': [1, 0, 1], 'start_priority': 0,
                'end_priority': 1}
        self.run_case(case)

    def test_forward_mechanism_locked_outbound_link(self):
        case = {'demands': [1, 0, 1], 'supplies': [1, 1, 0], 'outbound_links': [0, 1, 1], 'cum_term': [1, 1, 1],
                'expected_outflows': [1, 0, 0], 'expected_inflows': [1, 0, 0], 'start_priority': 0,
                'end_priority': 1}
        self.run_case(case)
    
    def run_case(self, case):
        node = self.create_node()
        node.start(1, 60)

        inbound_links = node.inbound_links
        outbound_links = node.outbound_links

        for u, demand in enumerate(case['demands']):
            inbound_links[u].get_demand = MagicMock(return_value=demand)
            
            if 'cum_term' in case:
                ret_val_cum = case['cum_term'][u]
            else:
                ret_val_cum = demand
            
            inbound_links[u].get_cumulative_demand_term = MagicMock(return_value = ret_val_cum)

            inbound_links[u].set_outflow = MagicMock(return_value=[f'vehicle_{u}'])
            inbound_links[u].get_vehicle_from_index = MagicMock(return_value=f'vehicle_{u}')

        
        for u, supply in enumerate(case['supplies']):
            outbound_links[u].get_supply = MagicMock(return_value=supply)
            outbound_links[u].set_inflow = MagicMock()
        
        node.get_outbound_vehicle_from_vehicle = MagicMock()
        node.get_outbound_vehicle_from_vehicle.side_effect = case['outbound_links']

        node.prepare_step(0)
        node.priority_index = case['start_priority']
        node.compute_flows(0)

        for u, expected_flow in enumerate(case['expected_inflows']):
            self.assertEqual(len(outbound_links[u].set_inflow.call_args[0][0]), expected_flow) 
        
        for u, expected_flow in enumerate(case['expected_outflows']):
            self.assertEqual(inbound_links[u].set_outflow.call_args[0][0], expected_flow)
        
        self.assertEqual(node.priority_index, case['end_priority'])

    def create_node(self):
        inbound_links = []

        for i in range(3):
            link = Link(link_id = i+1, length=300, kj=0.1, w=6.0, vf=30.0)
            inbound_links.append(link)
        
        outbound_links = []
        for i in range(3):
            link = Link(link_id = i+4, length=300, kj=0.1, w=6.0, vf=30.0)
            outbound_links.append(link)
        
        priorities = [0, 1, 2]
        node = GeneralNodeModel(1, inbound_links, outbound_links, priorities)
        return node



if __name__ == '__main__':
    unittest.main()