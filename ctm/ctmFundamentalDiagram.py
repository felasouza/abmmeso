

class CTMFundamentalDiagram:
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            self.__dict__[k] = v
    
    def get_flow(self, density):
        pass
    
    def get_speed(self, density):
        pass
    
    def get_demand(self, density):
        pass
    
    def get_supply(self, density):
        pass
    
    def get_capacity(self):
        pass
    
    def get_critical_density(self):
        pass
    
    def get_jam_density(self):
        pass