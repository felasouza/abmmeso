

class Link:
    def __init__(self, **kwargs):
        self.length = None
        self.vf = None
        self.w = None
        self.kj = None
        self.T1 = None
        self.T2 = None
        self.cap = None
        self.time_step = None
        self.total_time = None
        self.total_steps = None
        self.cumulative_inflows = None
        self.cumulative_outflows = None
        self.supplies = None
        self._inflow = None
        self._outflow = None
        self._demand = None
        self._supply = None


        for k,v in kwargs.items():
            setattr(self, k, v)

    
    def start(self, time_step, total_time):
        total_steps = int(total_time/time_step)
        self.total_steps = total_steps
        self.time_step = time_step
        self.total_time = total_time

        self.cumulative_inflows = [0 for _ in range(total_steps+1)]
        self.cumulative_outflows = [0 for _ in range(total_steps+1)]
        self.supplies = [0 for _ in range(total_steps+1)]

        self.T1 = max(1,int(self.length/(self.vf*time_step)))
        self.T2 = max(1, int(self.length/(self.w*time_step)))

        self.cap = self.kj*self.vf*self.w/(self.vf+self.w)
    

    def set_inflow(self, inflow):
        self._inflow = inflow

    def set_outflow(self, outflow):
        self._outflow = outflow

    def get_demand(self):
        return self._demand

    def get_supply(self):
        return self._supply

    def update_state_variables(self, t):
        self.cumulative_inflows[t+1] = self.cumulative_inflows[t] + self._inflow
        self.cumulative_outflows[t+1] = self.cumulative_outflows[t] + self._outflow

        self._demand = None
        self._supply = None
        self._inflow = None
        self._outflow = None

    def compute_demand_and_supplies(self, t):
        if t < self.T1-1:
            self._demand = 0
        else:
            self._demand = min(self.cumulative_inflows[t-self.T1+1]-self.cumulative_outflows[t], self.cap)

        if t < self.T2-1:
            self._supply = self.cap
        else:
            self._supply = min(self.kj*self.length- self.cumulative_outflows[t-self.T2-1]-self.cumulative_inflows[t], self.cap)