from ctm.ctmLink import CTMLink


class VariableLaneFDLink(CTMLink):
    def __init__(self, **kwargs):
        self.alpha_d = None
        super().__init__(**kwargs)
        self.fds_switches = []
        self.lanes_switches = []
        self.first_cell_demands = []

    def start(self, time_step, total_time):
        super().start(time_step, total_time)

        # Initialize the fundamental diagrams and lane counts
        self.fds_switches.append((0, self.fundamental_diagram))
        self.lanes_switches.append((0, self.num_lanes))

    def set_switch(self, time_step, fundamental_diagram, num_lanes):
        self.fds_switches.append((time_step, fundamental_diagram))
        self.lanes_switches.append((time_step, num_lanes))
        self.fundamental_diagram = fundamental_diagram
        self.num_lanes = num_lanes

    def compute_demand_and_supplies(self, step):
        super().compute_demand_and_supplies(step)

        # we change the demnad of the first cell
        for cell in range(self.num_cells):
            overcritical = (
                self.rho[cell, step] - self.fundamental_diagram.get_critical_density()
            )
            max_demand = (
                self.fundamental_diagram.get_capacity()
                * (
                    1
                    - self.alpha_d
                    * overcritical
                    / (
                        self.fundamental_diagram.get_jam_density()
                        - self.fundamental_diagram.get_critical_density()
                    )
                )
                * self.num_lanes
            )
            if cell == 0:
                self.demands[cell] = min(self.demands[cell], max_demand)
                self.first_cell_demands.append(max_demand)
