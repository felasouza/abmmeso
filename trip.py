import random

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
    def from_continuous_demand(cls, demand_pattern, total_time, route=None, route_integer_share = None, random_route=False):
        time_step_demand = total_time / len(demand_pattern)

        trips = []

        if route_integer_share is not None:
            share_sum = sum(route_integer_share.values())
            share_values = []

            for k,v in route_integer_share.items():
                share_values.extend([k for _ in range(v)])

        for i, demand in enumerate(demand_pattern):
            num_trips = int(time_step_demand*demand)
            trip_interval = time_step_demand / num_trips

            interval_trips = [cls(trip_id=len(trips)+u, origin=0, destination=0, start=time_step_demand*i+u*trip_interval, route=route) for u in range(num_trips)]


            if route_integer_share is not None:
                for u, trip in enumerate(interval_trips):
                    if random_route:
                        route = random.choice(share_values)
                    else:
                        route = share_values[(len(trips)+u)%share_sum]
                    trip.route = route

            trips.extend(interval_trips)


        return trips