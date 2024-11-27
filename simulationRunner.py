

class SimulationRunner:
    def __init__(self, **kwargs):
        self.links = None
        self.nodes = None
        self.time_step = None
        self.total_time = None

        for k,v in kwargs.items():
            setattr(self, k, v)
    
    def run(self):
        for link in self.links:
            link.start(self.time_step, self.total_time)
        
        for node in self.nodes:
            node.start(self.time_step, self.total_time)
        
        total_steps = int(self.total_time/self.time_step)

        for t in range(total_steps):
            for node in self.nodes:
                node.prepare_step(t)
            
            for link in self.links:
                link.compute_demand_and_supplies(t)
            
            for node in self.nodes:
                node.compute_flows(t)
            
            for link in self.links:
                link.update_state_variables(t)

    def get_times(self, added_step = 0):
        return list([i*self.time_step for i in range(int(self.total_time/self.time_step)+added_step)])


