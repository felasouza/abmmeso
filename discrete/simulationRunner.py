

class SimulationRunner:
    def __init__(self):
        self.demands_by_node = None
        self.links = None
        self.nodes = None
        self.time_step = None
        self.total_time = None
    
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
