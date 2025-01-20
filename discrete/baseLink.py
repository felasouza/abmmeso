class BaseLink:
    def __init__(self, **kwargs):
        self.link_id = None
        self.length = None

    def start(self, time_step, total_time):
        pass

    def set_inflow(self, vehicles):
        pass

    def set_outflow(self, num_vehicles):
        pass

    def get_capacity(self):
        return 0.0

    def get_demand(self):
        pass

    def get_next_step_demand(self):
        pass

    def get_supply(self):
        pass

    def get_cumulative_demand_term(self):
        pass

    def get_vehicle_from_index(self, index):
        pass

    def update_state_variables(self, t):
        pass

    def get_flows_in_the_past_steps(self, t, steps):
        pass

    def compute_demand_and_supplies(self, t):
        pass

    def get_output_records(self, time_step):
        return []
