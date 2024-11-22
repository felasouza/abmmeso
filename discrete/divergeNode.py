
class DivergeNode:
    def __init__(self, node_id, inbound_link, outbound_links):
        self.node_id = node_id
        self.inbound_link = inbound_link
        self.outbound_links = outbound_links
        self.total_time = None
        self.time_step = None
        self.total_steps = None

    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = total_time // time_step
    
    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        upstream_demand = self.inbound_link.get_demand()
        remaining_supplies = [link.get_supply() for link in self.outbound_links]
        vehicles_by_outbound_link = [[] for _ in self.outbound_links]
        total_flow = 0
        while True:
            if upstream_demand == 0:
                break

            front_vehicle = self.inbound_link.get_vehicle_from_index(total_flow)

            idx_outb = self.get_outbound_vehicle_from_vehicle(front_vehicle)

            if remaining_supplies[idx_outb] >= 1:
                remaining_supplies[idx_outb] -= 1
                total_flow += 1
                upstream_demand -= 1
                vehicles_by_outbound_link[idx_outb].append(front_vehicle)
            else:
                break
        
        ret_val = self.inbound_link.set_outflow(total_flow)
        for idx_outb, vehicles in enumerate(vehicles_by_outbound_link):
            self.outbound_links[idx_outb].set_inflow(vehicles)
        
        assert len(ret_val) == sum([len(vs) for vs in vehicles_by_outbound_link])

    def get_outbound_vehicle_from_vehicle(self, vehicle):
        pass