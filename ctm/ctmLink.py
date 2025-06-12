from continuousSingleCommodity.baseLink import BaseLink
import numpy

class CTMLink(BaseLink):
    
    def __init__(self, **kwargs):
        self.link_id = 0
        self.length = None
        self.fundamental_diagram = None
        self.time_step = None
        self.total_time = None
        self.total_steps = None
        self._inflow = None
        self._outflow = None
        self._demand = None
        self._supply = None
        self.total_steps = None
        self.time_step = None
        self.total_time = None
        self.rho = None
        self.qs = None
        self.demands = None
        self.supplies = None
        self.lm = None
        self.num_lanes = None
        self.num_cells = None


        for k,v in kwargs.items():
            setattr(self, k, v)


    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        total_steps = int(total_time/self.time_step)

        num_cells = int(self.length/self.lm)
        self.num_cells = num_cells

        self.rho = numpy.zeros((num_cells, total_steps+1))
        self.qs = numpy.zeros((num_cells, total_steps))

        self.demands = numpy.zeros((num_cells))
        self.supplies = numpy.zeros((num_cells))
        
        self._demand = 0.0
        self._supply = 0.0

    def compute_demand_and_supplies(self, step):
        for cell_index in range(self.num_cells):
            self.demands[cell_index] = self.num_lanes*self.fundamental_diagram.get_demand(self.rho[cell_index,step])
            self.supplies[cell_index] = self.num_lanes*self.fundamental_diagram.get_supply(self.rho[cell_index, step])
        
        self._supply = self.supplies[0]
        self._demand = self.demands[self.num_cells-1]
        
    def get_supply(self):
        return self._supply*self.time_step
    
    def get_demand(self):
        return self._demand*self.time_step

    def get_capacity(self):
        return self.fundamental_diagram.get_capacity()*self.num_lanes
    
    def get_jam_density(self):
        return self.fundamental_diagram.get_jam_density()*self.num_lanes

         
    def update_state_variables(self, step):

        for cell_index in range(self.num_cells):
            if cell_index==0:
                up_flow = self._inflow

            if cell_index < self.num_cells-1:
                flow = min(self.demands[cell_index], self.supplies[cell_index+1])
            else:
                flow = self._outflow

            self.qs[cell_index, step] = flow

            self.rho[cell_index,step+1] = self.rho[cell_index,step] + (up_flow-self.qs[cell_index, step])*self.time_step/(self.lm*self.num_lanes)

            up_flow = self.qs[cell_index, step]

    def set_inflow(self, inflow):
        self._inflow = inflow/self.time_step

    def set_outflow(self, outflow):
        self._outflow = outflow/self.time_step