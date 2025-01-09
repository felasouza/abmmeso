import json
from discrete.link import Link
from discrete.originNode import OriginNode
from discrete.destinationNode import DestinationNode
from discrete.divergeNode import DivergeNode
from discrete.mergeNode import MergeNode
from demand.trip import Trip
from simulationengine.simulationRunner import SimulationRunner

class JSONScenarioReader:
    node_handlers = {
        'OriginNode': "handle_origin_node",
        'DivergeNode': "handle_diverge_node",
        'MergeNode': "handle_merge_node",
        'DestinationNode': "handle_destination_node", 
    }
    def __init__(self, filename):
        self.filename = filename
        self.links_dic = {}
        self.nodes_dic = {}

    def get_simulation_runner(self):
        return self.simulation_runner
    
    def read(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)

        for link in data['links']:
            self.links_dic[link['link_id']] = Link(**link)

        
        for node in data['nodes']:
            method_name = self.node_handlers[node['node_type']]
            handler = getattr(self, method_name)
            self.nodes_dic[node['node_id']] = handler(node)
        
        self.total_time = data['total_time']
        self.time_step = data['time_step']
        links = list(self.links_dic.values())
        nodes = list(self.nodes_dic.values())
        self.simulation_runner = SimulationRunner(links=links, 
                                    nodes = nodes, total_time =self.total_time, 
                                    time_step = self.time_step)


    def parse_route(self, route_str):
        return tuple(map(int, route_str.strip("()").split(",")))

    def handle_origin_node(self, json_node):
        link = self.links_dic[json_node["link"]]
        if json_node['demand']['call'].lower() == "from_continuous_demand":
            steps = json_node['demand']['parameters']['demand_steps']
            route = json_node['demand']['parameters']["route"]
            random_route = json_node['demand']['parameters'].get("random_route", False)
            if 'route_integer_share' in json_node['demand']['parameters']:
                integer_share = json_node['demand']['parameters']['route_integer_share']
                route_integer_share = {}
                for route, integer_value in integer_share.items():
                    route = self.parse_route(route)
                    route_integer_share[route] = integer_value
                
                
                trips = Trip.from_continuous_demand(steps, json_node['demand']['parameters']['simulation_time'],
                route, route_integer_share, random_route)
                return OriginNode(json_node['node_id'], link, trips)
            else:
                pass


    def handle_diverge_node(self, json_node):
        node_id = json_node['node_id']
        inbound_link = self.links_dic[json_node['inbound_link']]
        outbound_links = [self.links_dic[link_id] for link_id in json_node['outbound_links']]
        return DivergeNode(node_id, inbound_link, outbound_links)

    def handle_merge_node(self, json_node):
        node_id = json_node['node_id']
        outbound_link = self.links_dic[json_node['outbound_link']]
        inbound_links = [self.links_dic[link_id] for link_id in json_node['inbound_links']]
        priority_vector = json_node['priority_vector']
        return MergeNode(node_id, outbound_link, inbound_links, priority_vector)

    def handle_destination_node(self, json_node):
        node_id = json_node['node_id']
        link = self.links_dic[json_node['link']]
        return DestinationNode(node_id, link)