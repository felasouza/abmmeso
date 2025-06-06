
import unittest

from ctm.triangularFundamentalDiagram import TriangularFundamentalDiagram

class TestTriangularFundamentalDiagram(unittest.TestCase):

    def setUp(self):
        # Initialize a Link object before each test
        self.fd = TriangularFundamentalDiagram(vf=30, kj=0.1, w=6.0)

    def test_base_values_computation(self):
        
        self.assertEqual(self.fd.get_jam_density(), 0.1)
        self.assertAlmostEqual(self.fd.get_flow(0.01), 0.01*30)
        self.assertAlmostEqual(self.fd.get_capacity(), 0.5)
        self.assertAlmostEqual(self.fd.get_critical_density(), 0.5/30.0)
        self.assertAlmostEqual(self.fd.get_speed(0.001), 30.0)
        self.assertAlmostEqual(self.fd.get_speed(self.fd.kj), 0.0)
        self.assertAlmostEqual(self.fd.get_demand(0.1), 0.5)
        self.assertAlmostEqual(self.fd.get_demand(0.25/30.0), 0.25)
        self.assertAlmostEqual(self.fd.get_supply(0.002), 0.5)
        self.assertAlmostEqual(self.fd.get_supply(0.1), 0.0)
        self.assertRaises(ValueError, self.fd.get_flow, -0.1)
        self.assertRaises(ValueError, self.fd.get_flow, self.fd.get_jam_density()+0.01)
        self.assertRaises(ValueError, self.fd.get_speed, -0.1)
        self.assertRaises(ValueError, self.fd.get_speed, self.fd.get_jam_density()+0.01)