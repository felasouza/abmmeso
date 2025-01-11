from .baseNode import BaseNode

class OriginNode(BaseNode):
    def __init__(self, node_id, link, demand_trips, **kwargs):
        self.node_id = node_id
        self.link = link
        self.demand_trips = demand_trips
        self.total_time = None
        self.time_step = None
        self.total_steps = None
        self.demands_at_steps = None
        self.entry_queue = None
        self.outflow = None

        for k,v in kwargs.items():
            setattr(self, k, v)
    

    def start(self, time_step, total_time):
        self.total_steps = int(total_time/time_step)
        self.time_step = time_step
        self.total_time = total_time
        self._demand = None

        self.entry_queue = [0 for _ in range(self.total_steps+1)]
        self.outflow = [0 for _ in range(self.total_steps)]
        self.vehicles = []
    
    def prepare_step(self, t):
        vehicles_departed = 0
        for vehicle in self.demand_trips:
            if vehicle.start <= t*self.time_step:
                vehicles_departed += 1
                self.vehicles.append(vehicle)
            else:
                break
        self.demand_trips = self.demand_trips[vehicles_departed:]
        self._demand = len(self.vehicles)

    def compute_flows(self, t):
        flow = min(self._demand, self.link.get_supply())
        if flow > 0:
            vehicles = self.vehicles[0:flow]
            self.vehicles = self.vehicles[flow:]
            self.link.set_inflow(vehicles)
        else:
            self.link.set_inflow([])
        self._demand = None
        self.entry_queue[t+1] = len(self.vehicles)
        self.outflow[t] = flow