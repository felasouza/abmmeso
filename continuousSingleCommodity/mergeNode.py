
class MergeNode:
    def __init__(self, node_id, inbound_links, outbound_link, priorities):
        self.node_id = node_id
        self.inbound_links = inbound_links
        self.outbound_link = outbound_link
        self.total_time = None
        self.time_step = None
        self.total_steps = None
        self.priorities = priorities
        #self.total_capacity = sum([link.cap for link in self.inbound_links])
        if len(self.inbound_links) != 2:
            raise ValueError("general cases not implemented yet")

    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = int(total_time / time_step)

    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        
        outbound_supply = self.outbound_link.get_supply()

        d0 = self.inbound_links[0].get_demand()
        d1 = self.inbound_links[1].get_demand()

        total_flow = 0
        
        g0 = min(d0, max(outbound_supply-d1, outbound_supply*self.priorities[0]))
        g1 = min(d1, max(outbound_supply-d0, outbound_supply*self.priorities[1]))
        total_flow = g0 + g1

        self.inbound_links[0].set_outflow(g0)
        self.inbound_links[1].set_outflow(g1)
        self.outbound_link.set_inflow(total_flow)