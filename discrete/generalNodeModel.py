from .baseNode import BaseNode


class GeneralNodeModel(BaseNode):
    def __init__(self, node_id, inbound_links, outbound_links, priority_vector):
        self.node_id = node_id
        self.inbound_links = inbound_links
        self.outbound_links = outbound_links
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
        remaining_supplies = [link.get_supply() for link in self.outbound_links]
        remaining_demands = [link.get_demand() for link in self.inbound_links]
        cumulative_terms = [
            link.get_cumulative_demand_term() for link in self.inbound_links
        ]

        flow_by_inbound_link = [0 for _ in self.inbound_links]
        total_flow = 0

        initial_index = self.priority_index

        flow_order_by_outbound_link = [[] for _ in self.outbound_links]
        priority_base = True
        locked_outbound_indices = []

        while True:

            if priority_base:
                iteration_index = self.priority_index
            idx = self.priority_vector[iteration_index]

            approach_with_priority = self.inbound_links[idx]
            if priority_base:
                if (
                    remaining_demands[idx] == 0
                    and cumulative_terms[idx] - flow_by_inbound_link[idx] > 0
                ):
                    priority_base = False
                    locked_outbound_indices.append(idx)
                    iteration_index = (iteration_index + 1) % len(self.priority_vector)
                    continue

                elif remaining_demands[idx] < 1:
                    self.priority_index = (self.priority_index + 1) % len(
                        self.priority_vector
                    )
                    if self.priority_index == initial_index:
                        break
                    continue
            else:
                if (
                    remaining_demands[idx] == 0
                    and cumulative_terms[idx] - flow_by_inbound_link[idx] > 0
                ):
                    locked_outbound_indices.append(idx)

                if remaining_demands[idx] == 0:
                    iteration_index = (iteration_index + 1) % len(self.priority_vector)
                    if iteration_index == initial_index:
                        break
                    continue

            inb_flow = flow_by_inbound_link[idx]
            outbound_index = self.get_outbound_vehicle_from_vehicle(
                approach_with_priority.get_vehicle_from_index(inb_flow)
            )
            downstream_supply = remaining_supplies[outbound_index]
            # if here now we check whether the flow is possible
            if downstream_supply >= 1 and outbound_index not in locked_outbound_indices:
                remaining_supplies[outbound_index] -= 1

                total_flow += 1
                remaining_demands[idx] -= 1
                vehicle = approach_with_priority.get_vehicle_from_index(inb_flow)
                flow_order_by_outbound_link[outbound_index].append(vehicle)
                flow_by_inbound_link[idx] += 1
                # flow was possible to update priority index

                if priority_base:
                    self.priority_index = (self.priority_index + 1) % len(
                        self.priority_vector
                    )
                    if self.priority_index == initial_index:
                        break
                else:
                    iteration_index = (iteration_index + 1) % len(self.priority_vector)
                    if iteration_index == initial_index:
                        break
            else:
                locked_outbound_indices.append(outbound_index)

                iteration_index = (iteration_index + 1) % len(self.priority_vector)
                if priority_base is False and iteration_index == initial_index:
                    break
                priority_base = False

        for idx_outb, flow in enumerate(flow_order_by_outbound_link):
            self.outbound_links[idx_outb].set_inflow(flow)

        for idx_inb, flow in enumerate(flow_by_inbound_link):
            self.inbound_links[idx_inb].set_outflow(flow)

    def get_outbound_vehicle_from_vehicle(self, vehicle):
        idx_current = -1

        for idx_current, link in enumerate(vehicle.route):
            if link in [link.link_id for link in self.inbound_links]:
                break

        outbound_id = vehicle.route[idx_current + 1]

        for idx_outb, link in enumerate(self.outbound_links):
            if link.link_id == outbound_id:
                return idx_outb
