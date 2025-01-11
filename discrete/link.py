import math


class Link:
    def __init__(self, **kwargs):
        self.link_id = None
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
        self.cap_disc_upstream = None
        self.cap_disc_downstream = None
        self.vehicles = []
        self.supplies = None
        self._inflow = None
        self._outflow = None
        self._demand = None
        self._supply = None
        self._cum_supply_term = None
        self._cum_demand_term = None
        self._next_step_demand = None
        self.initial_capacity = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def start(self, time_step, total_time):
        total_steps = int(total_time / time_step)
        self.total_steps = total_steps
        self.time_step = time_step
        self.total_time = total_time

        self.cumulative_inflows = [0 for _ in range(total_steps + 1)]
        self.cumulative_outflows = [0 for _ in range(total_steps + 1)]
        self.supplies = [0 for _ in range(total_steps + 1)]
        self.cap_disc_upstream = [0 for _ in range(total_steps + 1)]
        self.cap_disc_downstream = [0 for _ in range(total_steps + 1)]

        self.T1 = max(1, int(self.length / (self.vf * time_step)))
        self.T2 = max(1, int(self.length / (self.w * time_step)))

        self.cap = self.kj * self.vf * self.w / (self.vf + self.w)
        if self.initial_capacity is not None:
            self.cap_disc_upstream[0] = self.initial_capacity
            self.cap_disc_downstream[0] = self.initial_capacity
        else:
            self.cap_disc_upstream[0] = math.ceil(self.cap * self.time_step) + 1
            self.cap_disc_downstream[0] = math.ceil(self.cap * self.time_step) + 1

    def set_inflow(self, vehicles):
        self._inflow = len(vehicles)
        self.vehicles.extend(vehicles)

    def set_outflow(self, num_vehicles):
        self._outflow = num_vehicles
        return [self.vehicles.pop(0) for _ in range(num_vehicles)]

    def get_demand(self):
        return self._demand

    def get_next_step_demand(self):
        return self._next_step_demand

    def get_supply(self):
        return self._supply

    def get_cumulative_demand_term(self):
        return self._cum_demand_term

    def get_vehicle_from_index(self, index):
        return self.vehicles[index]

    def update_state_variables(self, t):
        self.cumulative_inflows[t + 1] = self.cumulative_inflows[t] + self._inflow
        self.cumulative_outflows[t + 1] = self.cumulative_outflows[t] + self._outflow

        self.cap_disc_upstream[t + 1] = min(
            self.cap_disc_upstream[t] - self._inflow + self.cap * self.time_step,
            math.ceil(self.cap * self.time_step) + 1,
        )
        self.cap_disc_downstream[t + 1] = min(
            self.cap_disc_downstream[t] - self._outflow + self.cap * self.time_step,
            math.ceil(self.cap * self.time_step) + 1,
        )

        self._demand = None
        self._supply = None
        self._inflow = None
        self._outflow = None

    def get_flows_in_the_past_steps(self, t, steps):
        return self.cumulative_outflows[t] - self.cumulative_outflows[t - steps]

    def compute_demand_and_supplies(self, t):
        if t < self.T1 - 1:
            self._demand = 0
            self._cum_demand_term = 0
            self._next_step_demand = 0
        else:
            self._demand = min(
                math.floor(
                    self.cumulative_inflows[t - self.T1 + 1]
                    - self.cumulative_outflows[t]
                ),
                math.floor(self.cap_disc_downstream[t]),
            )
            self._cum_demand_term = (
                self.cumulative_inflows[t - self.T1 + 1] - self.cumulative_outflows[t]
            )

            queue_addition = (
                self.cumulative_inflows[t - self.T1 + 2]
                - self.cumulative_inflows[t - self.T1 + 1]
            )

            if queue_addition > 0 or self._cum_demand_term > 0:
                self._next_step_demand = 1
            else:
                self._next_step_demand = 0

        if t < self.T2 - 1:
            self._supply = int(self.cap_disc_upstream[t])
        else:
            self._supply = min(
                math.floor(
                    self.kj * self.length
                    + self.cumulative_outflows[t - self.T2 + 1]
                    - self.cumulative_inflows[t]
                ),
                math.floor(self.cap_disc_upstream[t]),
            )
            self._supply = int(self._supply)
            self._cum_supply_term = math.floor(
                self.kj * self.length
                + self.cumulative_outflows[t - self.T2 + 1]
                - self.cumulative_inflows[t]
            )

    def get_output_records(self, time_step):
        total_steps = int(self.total_time / time_step)
        records = []

        for t in range(total_steps + 1):
            start_step = int((t * time_step) / self.time_step)
            next_st = min(int(((t + 1) * time_step) / self.time_step), len(self.cumulative_inflows)-1)

            if t == 0:
                cumulative_inflow = 0
                cumulative_outflow = 0
            else:
                cumulative_inflow = self.cumulative_inflows[start_step]
                cumulative_outflow = self.cumulative_outflows[start_step]

            if t < total_steps:
                inflow = (
                    self.cumulative_inflows[next_st]
                    - self.cumulative_inflows[start_step]
                ) / time_step

                outflow = (
                    self.cumulative_outflows[next_st]
                    - self.cumulative_outflows[start_step]
                ) / time_step
            else:
                inflow = None
                outflow = None

            record = {
                "time": t * time_step,
                "inflow": inflow,
                "outflow": outflow,
                "cumulative_inflow": cumulative_inflow,
                "cumulative_outflow": cumulative_outflow,
            }
            records.append(record)
        return records
