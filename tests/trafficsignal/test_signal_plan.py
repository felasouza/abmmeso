import unittest
from trafficsignal.signalPlan import SignalPlan

class TestSignalPlan(unittest.TestCase):

    def setUp(self):
        protected_intervals = {
            1: [[0, 25]],
            2: [[0, 8]],
            3: [[10, 30]],
            4: [[10, 30]]
        }
        
        permitted_intervals = {
            1: [],
            2: [[8, 30]],
            3: [],
            4: []
        }

        stop_permit_intervals = {
            1: [],
            2: [],
            3: [],
            4: [[0,10], [30, 60]]
        }

        self.signal_plan = SignalPlan(1, 60, 0, protected_intervals, permitted_intervals, stop_permit_intervals)


    def test_get_right_of_way(self):
        #tuples of (link_id, instant, expected_result)
        test_cases = [
            (1, 0, SignalPlan.PROTECTED),
            (1, 25, SignalPlan.FORBIDDEN),
            (1, 26, SignalPlan.FORBIDDEN),
            (2, 0, SignalPlan.PROTECTED),
            (2, 8, SignalPlan.PERMITTED),
            (2, 9, SignalPlan.PERMITTED),
            (2, 30, SignalPlan.FORBIDDEN),
            (3, 0, SignalPlan.FORBIDDEN),
            (3, 10, SignalPlan.PROTECTED),
            (3, 30, SignalPlan.FORBIDDEN),
            (3, 31, SignalPlan.FORBIDDEN),
            (4, 0, SignalPlan.STOP_PERMIT),
            (4, 10, SignalPlan.PROTECTED),
            (4, 30, SignalPlan.STOP_PERMIT),
            (4, 31, SignalPlan.STOP_PERMIT),
        ]

        for link_id, instant, expected_result in test_cases:
            self.assertEqual(self.signal_plan.get_right_of_way(link_id, instant), expected_result)

if __name__ == '__main__':
    unittest.main()
