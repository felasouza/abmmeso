from continuousSingleCommodity.baseNode import BaseNode

class CapacityDropMergeNode(BaseNode):
    def __init__(self, node_id, freeway_link, ramp_link, freeway_outbound_link, theta_l, theta_r):
        self.node_id = node_id
        self.freeway_link = freeway_link
        self.ramp_link = ramp_link
        self.freeway_outbound_link = freeway_outbound_link
        self.theta_l = theta_l
        self.theta_r = theta_r
        self.total_time = None
        self.time_step = None
        self.total_steps = None
        self.alphas = None


    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = int(total_time / time_step)
        self.alphas = [0.0 for _ in range(self.total_steps)]
    
    def prepare_step(self, t):
        pass
    
    def compute_flows(self, t):
        if self.ramp_link:
            ramp_demand = self.ramp_link.get_demand()
        else:
            ramp_demand = 0.0
        freeway_supply = self.freeway_outbound_link.get_supply()+self.theta_r*ramp_demand
        freeway_demand = self.freeway_link.get_demand()
        
        jam_density_diff = (self.freeway_link.get_jam_density() - self.freeway_outbound_link.get_jam_density())/self.freeway_link.get_jam_density()
        if jam_density_diff <= 0:
            self.alphas[t] = 1.0
        else:
            self.alphas[t] = max(1.0, 1+jam_density_diff / (self.theta_l * self.freeway_link.get_jam_density()))
        
        #self.alphas[t] = 1.0
        
        freeway_supply *= self.alphas[t]
        
        volume_freeway_link = min(freeway_supply, freeway_demand)

        self.freeway_link.set_outflow(volume_freeway_link-ramp_demand)
        self.ramp_link.set_outflow(ramp_demand)
        
        self.freeway_outbound_link.set_inflow(volume_freeway_link+ramp_demand)
        