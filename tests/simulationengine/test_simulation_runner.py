import unittest
from simulationengine.simulationRunner import SimulationRunner
from pathlib import Path
from unittest.mock import Mock
import csv
import os

class TestJsonSimulationRunner(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        files = [
            Path("tests/simulationengine/mock_output.csv"),
            Path("tests/simulationengine/mock_trip_output.csv"),
            Path("tests/simulationengine/trips.csv"),
        ]
        for file in files:
            if os.path.exists(file):
                os.remove(file)

    def test_outputs(self):
        nodes = [Mock(), Mock()]
        links = [Mock(), Mock()]

        runner = SimulationRunner(
            links=links, nodes=nodes, time_step=1.0, total_time=2.0
        )

        runner.link_output_sample_time = 1.0
        runner.output_link_file = Path("tests/simulationengine/mock_output.csv")
        runner.trip_output_file = Path("tests/simulationengine/mock_trip_output.csv")
        links[0].get_output_records.return_value = [
            {
                "time": 0,
                "link_id": 1,
                "inflow": 1,
                "outflow": 0,
                "cumulative_inflow": 0,
                "cumulative_outflow": 0,
            },
            {
                "time": 1,
                "link_id": 1,
                "inflow": 1,
                "outflow": 1,
                "cumulative_inflow": 1,
                "cumulative_outflow": 1,
            },
            {
                "time": 2,
                "link_id": 1,
                "inflow": 1,
                "outflow": 1,
                "cumulative_inflow": 2,
                "cumulative_outflow": 2,
            },
        ]

        links[1].get_output_records.return_value = [
            {
                "time": 0,
                "link_id": 2,
                "inflow": 0.5,
                "outflow": 0,
                "cumulative_inflow": 0,
                "cumulative_outflow": 0,
            },
            {
                "time": 1,
                "link_id": 2,
                "inflow": 0.5,
                "outflow": 0.5,
                "cumulative_inflow": 0.5,
                "cumulative_outflow": 0.5,
            },
            {
                "time": 2,
                "link_id": 2,
                "inflow": 0.5,
                "outflow": 0.5,
                "cumulative_inflow": 1,
                "cumulative_outflow": 1.0,
            },
        ]

        nodes[0].get_arrived_trips.return_value = [
            {"trip_id": 1, "origin": 1, "destination": 2, "start": 1, "end": 8}
        ]
        nodes[1].get_arrived_trips.return_value = [
            {"trip_id": 2, "origin": 1, "destination": 2, "start": 1, "end": 10},
            {"trip_id": 3, "origin": 1, "destination": 2, "start": 1, "end": 11},
        ]

        runner.write_outputs()

        with open(runner.output_link_file, "r") as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            self.assertEqual(len(rows), 6)
            self.assertEqual(int(rows[-1]["link_id"]), 2)
            self.assertAlmostEqual(float(rows[-1]["inflow"]), 0.5)

        with open(runner.trip_output_file, "r") as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            self.assertEqual(len(rows), 3)
            self.assertEqual(int(rows[0]["trip_id"]), 1)
            self.assertEqual(int(rows[1]["trip_id"]), 2)
            self.assertEqual(int(rows[2]["trip_id"]), 3)
            self.assertEqual(int(rows[2]["end"]), 11)
