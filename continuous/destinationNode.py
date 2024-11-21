

class DestinationNode:
    def __init__(self, node_id, link):
        self.node_id = node_id
        self.link = link
        self.total_time = None
        self.time_step = None
        self.total_steps = None
        self.inflow = []

    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = total_time // time_step

        self.inflow = [0] * self.total_steps

    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        outflow = self.link.get_demand()
        self.link.set_outflow(outflow)
        self.inflow[t] = outflow
