import unittest

from discrete.signalizedNode import SignalizedNode
from discrete.link import Link
from signalPlan import SignalPlan
from unittest.mock import MagicMock

class LinkDescriptor:
    def __init__(self, **kwargs):
        self.get_outflow = kwargs.get('get_outflow', 0)
        self.get_demand = kwargs.get('get_demand', 0)
        self.get_supply = kwargs.get('get_supply', 0)
        self.expected_inflow = kwargs.get('expected_inflow', [])
        self.expected_outflow = kwargs.get('expected_outflow', 0)
        self.get_vehicle_from_index = kwargs.get('get_vehicle_from_index', None)

class CaseDescriptor:
    def __init__(self, links, side_effect_right_of_way, side_effect_get_outbound_vehicle_from_vehicle, step):
        self.links = links
        self.side_effect_get_outbound_vehicle_from_vehicle = side_effect_get_outbound_vehicle_from_vehicle
        self.side_effect_right_of_way = side_effect_right_of_way
        self.step = step


class TestSignalizedNode(unittest.TestCase):

    def setUp(self):
        pass




    def test_only_protected_or_forbidden(self):
        links, node = self.get_links_and_nodes()

        for link in links:
            link.start(1, 60)
        node.start(1, 60)

        descriptor = CaseDescriptor(
            links=[
            LinkDescriptor(get_outflow=1, get_demand=1, get_supply=1, expected_inflow=1, expected_outflow=1, get_vehicle_from_index = ['vehicle_1']),
            LinkDescriptor(get_outflow=1, get_demand=1, get_supply=1, expected_inflow=1, expected_outflow=1, get_vehicle_from_index = ['vehicle_2']),
            LinkDescriptor(get_outflow=0, get_demand=1, get_supply=1, expected_inflow=0, expected_outflow=0, get_vehicle_from_index = ['vehicle_3']),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=0, expected_outflow=0),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=['vehicle_1'], expected_outflow=0),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=['vehicle_2'], expected_outflow=0),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=[], expected_outflow=0),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=[], expected_outflow=0)
            ],
            side_effect_right_of_way=[
            SignalPlan.PROTECTED, SignalPlan.PROTECTED, SignalPlan.FORBIDDEN, SignalPlan.STOP_PERMIT
            ],
            side_effect_get_outbound_vehicle_from_vehicle=[0, 1],
            step=6
        )
        self.run_descriptor(descriptor)
    
    def test_permitted_with_conflicting(self):
        links, node = self.get_links_and_nodes()

        for link in links:
            link.start(1, 60)
        node.start(1, 60)

        descriptor = CaseDescriptor(
            links=[
            LinkDescriptor(get_outflow=1, get_demand=1, get_supply=1, expected_inflow=0, expected_outflow=1, get_vehicle_from_index = ['vehicle_1']),
            LinkDescriptor(get_outflow=0, get_demand=1, get_supply=1, expected_inflow=0, expected_outflow=0, get_vehicle_from_index = ['vehicle_2']),
            LinkDescriptor(get_outflow=0, get_demand=1, get_supply=1, expected_inflow=0, expected_outflow=1, get_vehicle_from_index = ['vehicle_3']),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=0, expected_outflow=0),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=['vehicle_1'], expected_outflow=1),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=[], expected_outflow=0),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=['vehicle_3'], expected_outflow=0),
            LinkDescriptor(get_outflow=0, get_demand=0, get_supply=1, expected_inflow=[], expected_outflow=0)
            ],
            side_effect_right_of_way=[
            SignalPlan.PROTECTED, SignalPlan.PERMITTED, SignalPlan.PROTECTED, SignalPlan.STOP_PERMIT
            ],
            side_effect_get_outbound_vehicle_from_vehicle=[0, 2],
            step=14
        )
        self.run_descriptor(descriptor)

    def run_descriptor(self, descriptor):
        links, node = self.get_links_and_nodes()
        for link, link_descriptor in zip(links, descriptor.links):
            #link.get_outflow = MagicMock(return_value = link_descriptor.get_outflow)
            link.set_inflow = MagicMock()
            link.get_demand = MagicMock(return_value = link_descriptor.get_demand)
            link.get_supply = MagicMock(return_value = link_descriptor.get_supply)
            link.get_vehicle_from_index = MagicMock(side_effect = link_descriptor.get_vehicle_from_index)

        node.prepare_step(descriptor.step)
        node.signal_plan.get_right_of_way = MagicMock()
        node.signal_plan.get_right_of_way.side_effect = descriptor.side_effect_right_of_way
        node.get_outbound_vehicle_from_vehicle = MagicMock()
        node.get_outbound_vehicle_from_vehicle.side_effect = descriptor.side_effect_get_outbound_vehicle_from_vehicle
        node.compute_flows(descriptor.step)

        for link, link_descriptor in zip(links[0:4], descriptor.links[0:4]):
            link.set_outflow.assert_called_with(link_descriptor.expected_outflow)
        
        for link, link_descriptor in zip(links[4:], descriptor.links[4:]):
            link.set_inflow.assert_called_with(link_descriptor.expected_inflow)


    def get_links_and_nodes(self):
        #inbound links
        link_1 = Link(link_id=1, length=150, vf=15, w=6, kj=0.1)
        link_2 = Link(link_id=2, length=150, vf=15, w=6, kj=0.1)
        link_3 = Link(link_id=3, length=150, vf=15, w=6, kj=0.1)
        link_4 = Link(link_id=4, length=150, vf=15, w=6, kj=0.1)

        #outbound links
        link_5 = Link(link_id=5, length=150, vf=15, w=6, kj=0.1)
        link_6 = Link(link_id=6, length=150, vf=15, w=6, kj=0.1)
        link_7 = Link(link_id=7, length=150, vf=15, w=6, kj=0.1)
        link_8 = Link(link_id=8, length=150, vf=15, w=6, kj=0.1)

        all_links = [link_1, link_2, link_3, link_4, link_5, link_6, link_7, link_8]


        for link in all_links:
            link.set_outflow = MagicMock()
            link.set_outflow.side_effect = lambda x: [f'vehicle_{i}' for i in range(x)]


        inbound_links = [link_1, link_2, link_3, link_4]
        outbound_links = [link_5, link_6, link_7, link_8]

        conflicting_map = {1: [], 2: [3,4], 3: [2], 4:[2]}
        all_links = inbound_links + outbound_links
        signal_node = SignalizedNode(1, inbound_links, outbound_links, conflicting_map, self.get_signal_plan())
        return all_links, signal_node

    def get_signal_plan(self):
        #thinking on a link with thru (link 1), left (2) and the opposing thru (3) and right turn (4)
        
        protected_intervals = {
            1: [[0, 25]],
            2: [[0, 8]],
            3: [[10, 30]],
            4: [[10, 30]]
        }
        
        permitted_intervals = {
            1: [],
            2: [[8, 30]],
            3: [],
            4: []
        }

        stop_permit_intervals = {
            1: [],
            2: [],
            3: [],
            4: [[0,10], [30, 60]]
        }

        plan = SignalPlan(1, 60, 0, protected_intervals, permitted_intervals, stop_permit_intervals)
        return plan

if __name__ == '__main__':
    unittest.main()
