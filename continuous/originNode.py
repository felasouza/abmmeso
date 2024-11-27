

class OriginNode:
    def __init__(self, node_id, link, demands, **kwargs):
        self.node_id = node_id
        self.link = link
        self.demands = demands
        self.total_time = None
        self.time_step = None
        self.total_steps = None
        self.demands_at_steps = None
        self.entry_queue = None
        self.outflow = None

        for k,v in kwargs.items():
            setattr(self, k, v)
    

    def start(self, time_step, total_time):
        self.total_steps = int(total_time/time_step)
        self.time_step = time_step
        self.total_time = total_time
        self._demand = None


        self.demands_at_steps = [0 for _ in range(self.total_steps)]

        ratio_steps = int(self.total_steps/len(self.demands))
        for i in range(len(self.demands)):
            for j in range(ratio_steps):
                self.demands_at_steps[i*ratio_steps+j] = self.demands[i]*self.time_step

        self.entry_queue = [0 for _ in range(self.total_steps+1)]
        self.outflow = [0 for _ in range(self.total_steps)]
    
    def prepare_step(self, t):
        self._demand = self.demands_at_steps[t]+self.entry_queue[t]

    def compute_flows(self, t):
        flow = min(self._demand, self.link.get_supply())
        self.link.set_inflow(flow)
        self._demand = None
        self.entry_queue[t+1] = self.entry_queue[t] - flow + self.demands_at_steps[t]
        self.outflow[t] = flow