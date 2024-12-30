import unittest

from continuousSingleCommodity.link import Link  # Adjust the import based on the actual module structure

class TestContinuousLink(unittest.TestCase):

    def setUp(self):
        # Initialize a Link object before each test
        self.link = Link(length=300, kj=0.1, w=6.0, vf=30.0)
        self.link.start(time_step=1, total_time=3600)

    def test_initial_state(self):
        # Test the initial state of the Link object
        
        self.assertIsNotNone(self.link)
        # Add more assertions based on the initial state of the Link object

    def test_initial_demand(self):
        # Test a specific method of the Link class
        self.link.compute_demand_and_supplies(0)
        demand = self.link.get_demand()
        self.assertEqual(demand, 0)

        supply = self.link.get_supply()
        self.assertEqual(supply, 0.5)
    
    def test_demand_increase(self):
        self.link.start(time_step=1, total_time=30)
        for t in range(self.link.T1):
            self.link.compute_demand_and_supplies(t)
            self.assertEqual(self.link.get_demand(), 0)
            self.link.set_inflow(0.5)
            self.link.set_outflow(0)
            self.link.update_state_variables(t)
        
        self.link.compute_demand_and_supplies(self.link.T1)
        self.assertEqual(self.link.get_demand(), 0.5)
        self.assertEqual(self.link.cumulative_inflows[self.link.T1], 0.5*self.link.T1)
    
    def test_supply_decrease(self):
        self.link.start(time_step=1, total_time=180)
        inflow_plan = 0.4
        holding_capacity = self.link.kj*self.link.length
        required_steps = int(holding_capacity/inflow_plan)
        corrected_inflow = holding_capacity/required_steps
        for t in range(required_steps):
            self.link.compute_demand_and_supplies(t)
            self.assertGreaterEqual(self.link.get_supply(), corrected_inflow)
            self.link.set_inflow(corrected_inflow)
            self.link.set_outflow(0.0)
            self.link.update_state_variables(t)
        
        self.link.compute_demand_and_supplies(required_steps)
        self.assertAlmostEqual(self.link.get_supply(), 0)

    def test_supply_and_time_step(self):

        for time_step in [1.0, 3.0, 5.0]:
            link = Link(length=300, kj=0.1, w=6.0, vf=30.0)
            link.start(time_step=time_step, total_time=3600)

            for t in range(int(100/time_step)):
                link.compute_demand_and_supplies(t)
                if link.get_supply()-0.3*time_step < -0.01:
                    print(t, link.get_supply(), time_step)
                self.assertGreaterEqual(link.get_supply()-0.3*time_step, -0.01)
                link.set_inflow(min(link.get_supply(), 0.5*time_step))
                link.set_outflow(min(link.get_demand(), 0.3*time_step))
                link.update_state_variables(t)
                




    def tearDown(self):
        # Clean up after each test
        del self.link

if __name__ == '__main__':
    unittest.main()