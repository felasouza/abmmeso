

class DivergeNode:
    def __init__(self, node_id, inbound_link, outbound_links, turn_rates, **kwargs):
        self.node_id = node_id
        self.inbound_link = inbound_link
        self.outbound_links = outbound_links
        self.turn_rates = turn_rates
        self.total_time = None
        self.time_step = None
        self.total_steps = None

        for k,v in kwargs.items():
            setattr(self, k, v)
    
    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = total_time // time_step
        
    
    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        demand = self.inbound_link.get_demand()

        inbound_flow = demand

        for u, link in enumerate(self.outbound_links):
            supply = link.get_supply()
            inbound_flow = min(inbound_flow, supply/self.turn_rates[u])
        
        self.inbound_link.set_outflow(inbound_flow)
        for u, link in enumerate(self.outbound_links):
            link.set_inflow(inbound_flow*self.turn_rates[u])