

class BaseLink:
    def __init__(self, **kwargs):
        self.link_id = 0
        self.length = None

    def start(self, time_step, total_time):
        pass
    
    def compute_demand_and_supplies(self, t):
        pass
    
    def get_capacity(self):
        return 0.0

    def set_inflow(self, inflow):
        pass

    def set_outflow(self, outflow):
        pass

    def get_demand(self):
        pass
    def get_supply(self):
        pass
    
    def update_state_variables(self, t):
        pass

    def get_output_records(self, time_step):
        return []