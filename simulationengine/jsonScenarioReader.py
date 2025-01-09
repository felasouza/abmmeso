import json
import discrete.link
import discrete.originNode
import discrete.destinationNode
import discrete.divergeNode
import discrete.mergeNode
import continuousSingleCommodity.link
import continuousSingleCommodity.originNode
import continuousSingleCommodity.destinationNode
import continuousSingleCommodity.divergeNode
import continuousSingleCommodity.mergeNode
import demand.trip
import simulationengine.simulationRunner
import pathlib


class JSONScenarioReader:
    node_handlers_discrete = {
        "OriginNode": "handle_origin_node",
        "DivergeNode": "handle_diverge_node",
        "MergeNode": "handle_merge_node",
        "DestinationNode": "handle_destination_node",
    }

    node_handlers_continuous = {
        "OriginNode": "handle_origin_node_sc",
        "DivergeNode": "handle_diverge_node_sc",
        "MergeNode": "handle_merge_node_sc",
        "DestinationNode": "handle_destination_node_sc",
    }

    def __init__(self, filename):
        self.filename = filename
        self.links_dic = {}
        self.nodes_dic = {}
        self.data = None
        self.trips = None

    def get_simulation_runner(self):
        return self.simulation_runner

    def read(self):
        with open(self.filename, "r") as f:
            self.data = json.load(f)

        if self.data["modeling_type"] == "discrete":
            node_handler = self.node_handlers_discrete

            trip_file = self.data.get("trip_file", None)
            if trip_file is not None:
                main_path = pathlib.Path(self.filename)
                trip_file_path = main_path.parent / trip_file

                with open(trip_file_path, "r") as f:
                    self.trips = json.load(f)["trips"]
        else:
            node_handler = self.node_handlers_continuous

        for link in self.data["links"]:
            if self.data["modeling_type"] == "discrete":
                self.links_dic[link["link_id"]] = discrete.link.Link(**link)
            else:
                self.links_dic[link["link_id"]] = continuousSingleCommodity.link.Link(
                    **link
                )

        for node in self.data["nodes"]:
            method_name = node_handler[node["node_type"]]
            handler = getattr(self, method_name)
            self.nodes_dic[node["node_id"]] = handler(node)

        self.total_time = self.data["total_time"]
        self.time_step = self.data["time_step"]
        links = list(self.links_dic.values())
        nodes = list(self.nodes_dic.values())
        self.simulation_runner = simulationengine.simulationRunner.SimulationRunner(
            links=links,
            nodes=nodes,
            total_time=self.total_time,
            time_step=self.time_step,
        )

    def parse_route(self, route_str):
        return tuple(map(int, route_str.strip("()").split(",")))

    def handle_origin_node(self, json_node):
        link = self.links_dic[json_node["link"]]
        if (
            json_node["demand"] is not None
            and json_node["demand"]["call"].lower() == "from_continuous_demand"
        ):
            steps = json_node["demand"]["demand_steps"]
            route = json_node["demand"]["route"]
            random_route = json_node["demand"].get("random_route", False)
            if "route_integer_share" in json_node["demand"]:
                integer_share = json_node["demand"]["route_integer_share"]
                route_integer_share = {}
                for route, integer_value in integer_share.items():
                    route = self.parse_route(route)
                    route_integer_share[route] = integer_value

                time = json_node["demand"].get("simulation_time", None)
                if time is None:
                    time = self.data["total_time"]

                trips = demand.trip.Trip.from_continuous_demand(
                    steps, time, route, route_integer_share, random_route
                )
                return discrete.originNode.OriginNode(json_node["node_id"], link, trips)
        else:
            if self.trips is not None:
                trips_json = [
                    trip
                    for trip in self.trips
                    if trip["origin"] == json_node["link"]
                ]
                trips = [demand.trip.Trip(**trip) for trip in trips_json]
                trips.sort(key=lambda x: x.start)
                return discrete.originNode.OriginNode(
                    json_node["node_id"], link, trips
                )
            else:
                raise Exception("No trips file provided")

    def handle_origin_node_sc(self, json_node):
        node_id = json_node["node_id"]
        link = self.links_dic[json_node["link"]]
        demand_steps = json_node["demand_steps"]

        return continuousSingleCommodity.originNode.OriginNode(
            node_id, link, demand_steps
        )

    def handle_diverge_node(self, json_node):
        node_id = json_node["node_id"]
        inbound_link = self.links_dic[json_node["inbound_link"]]
        outbound_links = [
            self.links_dic[link_id] for link_id in json_node["outbound_links"]
        ]
        return discrete.divergeNode.DivergeNode(node_id, inbound_link, outbound_links)

    def handle_diverge_node_sc(self, json_node):
        node_id = json_node["node_id"]
        inbound_link = self.links_dic[json_node["inbound_link"]]
        outbound_links = [
            self.links_dic[link_id] for link_id in json_node["outbound_links"]
        ]
        turn_rates = json_node["turn_rates"]
        return continuousSingleCommodity.divergeNode.DivergeNode(
            node_id, inbound_link, outbound_links, turn_rates
        )

    def handle_merge_node(self, json_node):
        node_id = json_node["node_id"]
        outbound_link = self.links_dic[json_node["outbound_link"]]
        inbound_links = [
            self.links_dic[link_id] for link_id in json_node["inbound_links"]
        ]
        priority_vector = json_node["priority_vector"]
        return discrete.mergeNode.MergeNode(
            node_id, outbound_link, inbound_links, priority_vector
        )

    def handle_merge_node_sc(self, json_node):
        node_id = json_node["node_id"]
        outbound_link = self.links_dic[json_node["outbound_link"]]
        inbound_links = [
            self.links_dic[link_id] for link_id in json_node["inbound_links"]
        ]
        priorities = json_node["priorities"]
        return continuousSingleCommodity.mergeNode.MergeNode(
            node_id, inbound_links, outbound_link, priorities
        )

    def handle_destination_node(self, json_node):
        node_id = json_node["node_id"]
        link = self.links_dic[json_node["link"]]
        return discrete.destinationNode.DestinationNode(node_id, link)

    def handle_destination_node_sc(self, json_node):
        node_id = json_node["node_id"]
        link = self.links_dic[json_node["link"]]
        return continuousSingleCommodity.destinationNode.DestinationNode(node_id, link)
