from .baseNode import BaseNode


class DestinationNode(BaseNode):
    def __init__(self, node_id, link):
        self.node_id = node_id
        self.link = link
        self.total_time = None
        self.time_step = None
        self.total_steps = None
        self.inflow = []
        self.arrived_vehicles = []

    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = int(total_time / time_step)

        self.inflow = [0] * self.total_steps

    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        outflow = self.link.get_demand()
        vehicles = self.link.set_outflow(outflow)
        for vehicle in vehicles:
            vehicle.end = t
        self.inflow[t] = outflow
        self.arrived_vehicles.extend(vehicles)

    def get_arrived_trips(self):
        records = []
        for vehicle in self.arrived_vehicles:
            records.append(
                {
                    "trip_id": vehicle.trip_id,
                    "origin": vehicle.origin,
                    "destination": vehicle.destination,
                    "start": vehicle.start,
                    "end": vehicle.end,
                }
            )
        return records
