from .ctmFundamentalDiagram import CTMFundamentalDiagram

class TriangularFundamentalDiagram(CTMFundamentalDiagram):
    def __init__(self, **kwargs):
        self.vf = None
        self.w = None
        self.kj = None
        super().__init__(**kwargs)
        self._kc = self.kj*self.w/(self.w+self.vf)
        self._cap = self._kc*self.vf
    
    def get_flow(self, density):
        if density < 0 or density > self.kj:
            raise ValueError("Density must be in the range [0, kj]")
        return min(density*self.vf, self.w*(self.kj-density))
    
    def get_speed(self, density):
        if density < 0 or density > self.kj:
            raise ValueError("Density must be in the range [0, kj]")
        if density <= self._kc:
            return self.vf

        return self.w*(self.kj-density)        
    
    def get_demand(self, density):
        return self.get_flow(min(density, self._kc))
    
    def get_supply(self, density):
        return self.get_flow(max(self._kc, density))
    
    def get_capacity(self):
        return self._cap
    
    def get_critical_density(self):
        return self._kc
    
    def get_jam_density(self):
        return self.kj