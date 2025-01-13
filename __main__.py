import sys
import os
import pathlib

if __name__ == '__main__':
    print(os.getcwd() + '/abmmeso')
    sys.path.append(os.getcwd() + '/abmmeso')
    from simulationengine.jsonScenarioReader import JSONScenarioReader
    path = pathlib.Path(sys.argv[1])
    reader = JSONScenarioReader(path)
    reader.read()
    simulation_runner = reader.get_simulation_runner()
    simulation_runner.run()