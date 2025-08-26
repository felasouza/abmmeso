
import unittest

from ctm.triangularFundamentalDiagram import TriangularFundamentalDiagram
from ctm.variableLaneFDLink import VariableLaneFDLink

class TestVariableLaneFDLink(unittest.TestCase):

    def setUp(self):
        self.fd = TriangularFundamentalDiagram(vf=30, kj=0.1, w=6.0)
        self.link = VariableLaneFDLink(link_id=1, length=300, fundamental_diagram=self.fd, num_lanes=1, lm=30)
        self.link.alpha_d = 0.5
        self.link.start(time_step=1, total_time=10)

    def test_start(self):
        self.assertEqual(len(self.link.fds_switches), 1)
        self.assertEqual(len(self.link.lanes_switches), 1)
        self.assertEqual(self.link.fds_switches[0], (0, self.fd))
        self.assertEqual(self.link.lanes_switches[0], (0, 1))

    def test_set_switch(self):
        new_fd = TriangularFundamentalDiagram(vf=40, kj=0.2, w=7.0)
        self.link.set_switch(5, new_fd, 2)
        self.assertEqual(len(self.link.fds_switches), 2)
        self.assertEqual(len(self.link.lanes_switches), 2)
        self.assertEqual(self.link.fds_switches[1], (5, new_fd))
        self.assertEqual(self.link.lanes_switches[1], (5, 2))
        self.assertEqual(self.link.fundamental_diagram, new_fd)
        self.assertEqual(self.link.num_lanes, 2)

    def test_compute_demand_and_supplies_overcritical(self):
        # Set density to be overcritical
        self.link.rho[0, 0] = self.fd.get_critical_density() + 0.01
        
        self.link.compute_demand_and_supplies(0)

        # Manually calculate the expected max_demand
        overcritical = self.link.rho[0, 0] - self.fd.get_critical_density()
        expected_max_demand = (self.fd.get_capacity() * 
                               (1 - self.link.alpha_d * overcritical / 
                                (self.fd.get_jam_density() - self.fd.get_critical_density())))
        
        self.assertAlmostEqual(self.link.demands[0], expected_max_demand)
        self.assertAlmostEqual(self.link.first_cell_demands[0], expected_max_demand)

    def test_compute_demand_and_supplies_undercritical(self):
        # Set density to be undercritical
        self.link.rho[0, 0] = self.fd.get_critical_density() - 0.01
        
        self.link.compute_demand_and_supplies(0)

        # When undercritical, the demand should not be affected by the alpha_d logic
        self.assertAlmostEqual(self.link.demands[0], self.link.rho[0, 0] * self.fd.vf)

if __name__ == '__main__':
    unittest.main()
