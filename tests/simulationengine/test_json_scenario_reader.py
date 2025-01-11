import unittest
import simulationengine.jsonScenarioReader
from continuousSingleCommodity.link import Link
from pathlib import Path

class TestJsonScenarioReader(unittest.TestCase):
    def setUp(self):
        pass


    def test_sample_discrete(self):
        reader = simulationengine.jsonScenarioReader.JSONScenarioReader(Path("tests/simulationengine/sample.json").resolve())
        reader.read()
        runner = reader.get_simulation_runner()
        self.assertEqual(len(runner.nodes), 4)
        self.assertEqual(len(runner.links), 4)
        self.assertEqual(runner.total_time, 600)
        self.assertEqual(runner.time_step, 1)
        runner.run()
        times = runner.get_times()
        self.assertEqual(times, [i for i in range(600)])
        total_flow = ((0.2+0.5+0.8)/3)*600
        self.assertAlmostEqual(runner.links[0].cumulative_inflows[-1], total_flow)

    def test_sample_singlecommodity(self):
        reader = simulationengine.jsonScenarioReader.JSONScenarioReader(Path("tests/simulationengine/sample_single_commodity.json").resolve())
        reader.read()
        runner = reader.get_simulation_runner()
        self.assertEqual(len(runner.nodes), 4)
        self.assertEqual(len(runner.links), 4)
        self.assertTrue(isinstance(runner.links[0], Link))
        self.assertEqual(runner.total_time, 600)
        self.assertEqual(runner.time_step, 1)
        runner.run()
        times = runner.get_times()
        self.assertEqual(times, [i for i in range(600)])
        total_flow = ((0.2+0.5+0.8)/3)*600
        self.assertAlmostEqual(runner.links[0].cumulative_inflows[-1], total_flow)
    
    def test_trip_based_discrete(self):
        reader = simulationengine.jsonScenarioReader.JSONScenarioReader(Path("tests/simulationengine/sample_trip_based.json").resolve())
        reader.read()
        self.assertEqual(len(reader.nodes_dic[1].demand_trips), 20)
