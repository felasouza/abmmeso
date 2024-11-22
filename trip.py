

class Trip:
    def __init__(self, **kwargs):
        self.trip_id = 0
        self.origin = 0
        self.destination = 0
        self.start = 0
        self.route = []
        self.end = None
        self.travel_times = []

        for k,v in kwargs.items():
            setattr(self, k, v)
    
    @classmethod
    def from_continuous_demand(cls, demand_pattern, total_time, route=None):
        time_step_demand = total_time / len(demand_pattern)

        trips = []

        for i, demand in enumerate(demand_pattern):
            num_trips = int(time_step_demand*demand)
            trip_interval = time_step_demand / num_trips
            interval_trips = [cls(trip_id=len(trips)+u, origin=0, destination=0, start=time_step_demand*i+u*trip_interval, route=route) for u in range(num_trips)]
            trips.extend(interval_trips)

        return trips