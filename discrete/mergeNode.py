from .baseNode import BaseNode


class MergeNode(BaseNode):
    def __init__(self, node_id, outbound_link, inbound_links, priority_vector):
        self.node_id = node_id
        self.outbound_link = outbound_link
        self.inbound_links = inbound_links
        self.priority_vector = priority_vector
        self.priority_index = 0
        self.total_time = None
        self.time_step = None
        self.total_steps = None

    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = int(total_time / time_step)

    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        downstream_supply = self.outbound_link.get_supply()
        remaining_demands = [link.get_demand() for link in self.inbound_links]
        cumulative_terms = [
            link.get_cumulative_demand_term() for link in self.inbound_links
        ]

        flow_by_inbound_link = [0 for _ in self.inbound_links]
        total_flow = 0

        initial_index = self.priority_index
        inflow_order = []

        while True:
            idx = self.priority_vector[self.priority_index]
            approach_with_priority = self.inbound_links[
                self.priority_vector[self.priority_index]
            ]
            if (
                remaining_demands[idx] == 0
                and cumulative_terms[idx] - flow_by_inbound_link[idx] > 0
            ):
                break
            elif remaining_demands[idx] < 1:
                self.priority_index = (self.priority_index + 1) % len(
                    self.priority_vector
                )
                if self.priority_index == initial_index:
                    break
                continue

            # if here now we check whether the flow is possible
            if downstream_supply >= 1:
                downstream_supply -= 1

                total_flow += 1
                remaining_demands[self.priority_vector[self.priority_index]] -= 1
                inflow_order.append(
                    approach_with_priority.get_vehicle_from_index(
                        flow_by_inbound_link[self.priority_vector[self.priority_index]]
                    )
                )
                flow_by_inbound_link[self.priority_vector[self.priority_index]] += 1
                # flow was possible to update priority index
                self.priority_index = (self.priority_index + 1) % len(
                    self.priority_vector
                )
                if self.priority_index == initial_index:
                    break
            else:
                break

        self.outbound_link.set_inflow(inflow_order)

        for idx_inb, flow in enumerate(flow_by_inbound_link):
            self.inbound_links[idx_inb].set_outflow(flow)
