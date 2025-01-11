
class BaseNode:
    def __init__(
        self,
    ):
        self.node_id = 0

    def start(self, time_step, total_time):
        pass

    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        pass
