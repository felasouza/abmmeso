from continuousSingleCommodity.baseLink import BaseLink


class CTMLink(BaseLink):
    
    def __init__(self, **kwargs):
        self.link_id = 0
        self.length = None
        self.fundamental_diaram = None
        self.time_step = None
        self.total_time = None
        self.total_steps = None
        self._inflow = None
        self._outflow = None
        self._demand = None
        self._supply = None


        for k,v in kwargs.items():
            setattr(self, k, v)
