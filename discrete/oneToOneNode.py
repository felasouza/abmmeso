
class OneToOneNode:
    def __init__(self, node_id, inbound_link, outbound_link):
        self.node_id = node_id
        self.inbound_link = inbound_link
        self.outbound_link = outbound_link
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
        flow = min(self.inbound_link.get_demand(), self.outbound_link.get_supply())
        vehicles = self.inbound_link.set_outflow(flow)
        self.outbound_link.set_inflow(vehicles)
