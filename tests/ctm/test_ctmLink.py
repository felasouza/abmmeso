
import unittest

from ctm.triangularFundamentalDiagram import TriangularFundamentalDiagram
from ctm.ctmLink import CTMLink

class TestCTMLink(unittest.TestCase):

    def setUp(self):
        # Initialize a Link object before each test
        self.fd = TriangularFundamentalDiagram(vf=30, kj=0.1, w=6.0)
    
    def test_initialization(self):
        
        link = CTMLink(link_id=1, length=300, fundamental_diagram=self.fd, num_lanes=1, lm=30)
        
        link.start(time_step=1, total_time=10)
        self.assertEqual(link.rho.shape, (10, 11))
        self.assertEqual(link.qs.shape, (10, 10))
        self.assertEqual(link.num_cells, 10)
        self.assertEqual(link.time_step, 1)  

        link.start(time_step=2, total_time=60)
        self.assertEqual(link.rho.shape, (10, 31))
        self.assertEqual(link.qs.shape, (10, 30))
        self.assertEqual(link.num_cells, 10)
    
    def test_compute_demand_supplies(self):
        link = CTMLink(link_id=1, length=300, fundamental_diagram=self.fd, num_lanes=1, lm=30)
        link.start(time_step=1, total_time=10)
        
        link.rho[:, 0] = [self.fd._kc] * 10
        link.compute_demand_supplies(0) 
        self.assertAlmostEqual(link._demand, self.fd.get_capacity())
        self.assertAlmostEqual(link._supply, self.fd.get_capacity())
        
    def test_state_update(self):
        link = CTMLink(link_id=1, length=300, fundamental_diagram=self.fd, num_lanes=1, lm=30)
        link.start(time_step=1, total_time=10)
        
        link._inflow = 0.5
        link._outflow = 0.0
        link.rho[:, 0] = [0.0] * 10
        link.update(0)
        
        expected_rho = [0.0] * 10
        expected_rho[0] = 0.5/30.0
        
        for i in range(link.num_cells):
            self.assertEqual(link.rho[i, 1], expected_rho[i])

