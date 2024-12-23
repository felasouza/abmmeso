import unittest
from discrete.link import Link
from trip import Trip

def vehicle_trip(trip_id, step):
    return Trip(trip_id=trip_id, origin=1, destination=2, start=step, route=[1,], end=step+1, travel_times=[])

class TestLink(unittest.TestCase):

    def setUp(self):
        self.link = Link(length=300, kj=0.1, w=6.0, vf=30.0)
        self.link.start(time_step=1, total_time=3600)

    def test_initial_state(self):
        self.assertIsNotNone(self.link)
        self.assertEqual(self.link.length, 300)
        self.assertEqual(self.link.kj, 0.1)
        self.assertEqual(self.link.w, 6.0)
        self.assertEqual(self.link.vf, 30.0)
        self.assertEqual(self.link.time_step, 1)
        self.assertEqual(self.link.total_time, 3600)
        self.assertEqual(self.link.total_steps, 3600)

    def test_initial_demand(self):
        self.link.compute_demand_and_supplies(0)
        demand = self.link.get_demand()
        self.assertEqual(demand, 0)

        supply = self.link.get_supply()
        self.assertEqual(supply, self.link.cap_disc_upstream[0])

    def test_demand_increase(self):
        self.link.start(time_step=1, total_time=30)
        total_vehicles = 0
        for t in range(self.link.T1):
            self.link.compute_demand_and_supplies(t)
            if self.link._supply >= 1.0:
                self.link.set_inflow([vehicle_trip(total_vehicles, t)])
                total_vehicles += 1
            else:
                self.link.set_inflow([])
            self.link.set_outflow(0)
            self.link.update_state_variables(t)
            self.assertEqual(self.link.cumulative_inflows[t+1]-self.link.cumulative_outflows[t+1], len(self.link.vehicles))
        
        self.link.compute_demand_and_supplies(self.link.T1)
        self.assertEqual(self.link.get_demand(), 1.0)
        self.assertEqual(self.link.cumulative_inflows[self.link.T1], self.link.T1/2+1)

        len_before = len(self.link.vehicles)

        vehicle = self.link.set_outflow(1)
        self.assertEqual(vehicle[0].trip_id, 0)
        self.assertEqual(len(self.link.vehicles), len_before-1)
        
    
    def test_supply_decrease(self):
        self.link.start(time_step=1, total_time=180)
        inflow_plan = 0.5
        holding_capacity = self.link.kj * self.link.length
        required_steps = int(holding_capacity / inflow_plan)
        total_vehicles = 0
        for t in range(required_steps):
            self.link.compute_demand_and_supplies(t)
            if t%2 == 0:
                self.link.set_inflow([vehicle_trip(t, t)])
                total_vehicles += 1
            else:
                self.link.set_inflow([])
            self.assertGreaterEqual(self.link.get_supply(), 0)
            self.link.set_outflow(0)
            self.link.update_state_variables(t)

        self.link.compute_demand_and_supplies(required_steps)
        self.assertAlmostEqual(self.link.get_supply(), 0)

    def test_get_last_flows_and_future_demand(self):
        link = Link(length=150, kj=0.2, w=6.0, vf=30.0)

        link.start(time_step=1, total_time=30)

        for i in range(5):
            link.compute_demand_and_supplies(i)
            link.set_inflow([vehicle_trip(i, i)])
            link.set_outflow(0)
            link.update_state_variables(i)
        
        self.assertEqual(link.get_next_step_demand(),1)
        for i in range(5,10):
            link.compute_demand_and_supplies(i)
            link.set_inflow([])
            link.set_outflow(1)
            link.update_state_variables(i)
        

        self.assertEqual(link.get_flows_in_the_past_steps(10, 5), 5)
        self.assertEqual(link.get_flows_in_the_past_steps(10, 1), 1)





    def tearDown(self):
        del self.link

if __name__ == '__main__':
    unittest.main()