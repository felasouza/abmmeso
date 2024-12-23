from discrete.divergeNode import DivergeNode
from signalPlan import SignalPlan

class SignalizedNode(DivergeNode):
    def __init__(self, node_id, inbound_links, outbound_links, conflicting_map, signal_plan, **kwargs):
        self.node_id = node_id
        self.inbound_links = inbound_links
        self.outbound_links = outbound_links
        self.conflicting_map = conflicting_map
        self.signal_plan = signal_plan
        self.current_flows = {link.link_id: 0 for link in self.inbound_links}
        self.last_update = None
        self.permitted_flow_time = 0
        self.permitted_flow_steps = None

        for k,v in kwargs.items():
            setattr(self, k, v)

    def start(self, time_step, total_time):
        self.total_steps = int(total_time/time_step)
        self.time_step = time_step
        self.total_time = total_time
        self.last_update = -1
        self.permitted_flow_steps = int(self.permitted_flow_time/time_step)

    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        
        right_of_ways = {link.link_id: self.signal_plan.get_right_of_way(link.link_id, t) for link in self.inbound_links}

        priority_links = [link for link in self.inbound_links if right_of_ways[link.link_id] == SignalPlan.PROTECTED]

        permitted_links = [link for link in self.inbound_links if right_of_ways[link.link_id] == SignalPlan.PERMITTED]

        stop_permit_links = [link for link in self.inbound_links if right_of_ways[link.link_id] == SignalPlan.STOP_PERMIT]

        self.current_flows = {link.link_id: 0 for link in self.inbound_links}
        self.inflow_order_by_outbound_link = {link.link_id: [] for link in self.outbound_links}

        self.remaining_supplies = [link.get_supply() for link in self.outbound_links]

        self.compute_for_links(priority_links, True) #although not strictly necessary if the conflicting flows only affects the current step, but it is a good practice to avoid future errors
        self.compute_for_links(permitted_links)
        self.compute_for_links(stop_permit_links)

        for link in self.inbound_links:
            link.set_outflow(self.current_flows[link.link_id])
        
        for link in self.outbound_links:
            link.set_inflow(self.inflow_order_by_outbound_link[link.link_id])
        self.last_update = t

    def compute_for_links(self, links_with_row, protected=False):
        for link in links_with_row:
            demand = link.get_demand()

            if not protected:
                has_conflicting_flow = False
                for conflicting_link_id in self.conflicting_map[link.link_id]:
                    the_conflicting_link = [link for link in self.inbound_links if link.link_id == conflicting_link_id][0]
                    if self.current_flows[conflicting_link_id] > 0 or the_conflicting_link.get_next_step_demand() > 0 or the_conflicting_link.get_flows_in_the_past_steps(self.last_update, self.permitted_flow_steps) > 0:
                        has_conflicting_flow = True
                        break
            else:
                has_conflicting_flow = False
            
            if has_conflicting_flow:
                continue


            while demand >= 1:
                front_vehicle = link.get_vehicle_from_index(self.current_flows[link.link_id])
                idx_outb = self.get_outbound_vehicle_from_vehicle(front_vehicle)

                if self.remaining_supplies[idx_outb] >= 1:
                    self.remaining_supplies[idx_outb] -= 1
                    self.current_flows[link.link_id] += 1
                    demand -= 1
                    self.inflow_order_by_outbound_link[self.outbound_links[idx_outb].link_id].append(front_vehicle)
                else:
                    break


    def get_outbound_vehicle_from_vehicle(self, vehicle):
        idx_current = -1

        for idx_current, link in enumerate(vehicle.route):
            if link in [link.link_id for link in self.inbound_links]:
                break

        outbound_id = vehicle.route[idx_current+1]

        for idx_outb, link in enumerate(self.outbound_links):
            if link.link_id == outbound_id:
                return idx_outb