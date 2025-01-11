import csv
import pathlib


class SimulationRunner:
    def __init__(self, **kwargs):
        self.links = None
        self.nodes = None
        self.time_step = None
        self.total_time = None
        self.output_link_file = None
        self.trip_output_file = None
        self.link_output_sample_time = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def run(self):
        for link in self.links:
            link.start(self.time_step, self.total_time)

        for node in self.nodes:
            node.start(self.time_step, self.total_time)

        total_steps = int(self.total_time / self.time_step)

        for t in range(total_steps):
            for node in self.nodes:
                node.prepare_step(t)

            for link in self.links:
                link.compute_demand_and_supplies(t)

            for node in self.nodes:
                node.compute_flows(t)

            for link in self.links:
                link.update_state_variables(t)

        self.write_outputs()

    def get_times(self, added_step=0):
        return list(
            [
                i * self.time_step
                for i in range(int(self.total_time / self.time_step) + added_step)
            ]
        )

    def write_outputs(self):
        if self.output_link_file:
            all_records = []
            if self.link_output_sample_time is None:
                self.link_output_sample_time = min(self.total_time, 60)
            for link in self.links:
                all_records.extend(
                    link.get_output_records(self.link_output_sample_time)
                )

            with open(self.output_link_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=all_records[0].keys())
                writer.writeheader()
                writer.writerows(all_records)
        
        if self.trip_output_file:
            all_records = []
            
            for node in self.nodes:
                if "get_arrived_trips" in node.__class__.__dict__:
                    all_records.extend([el for el in node.get_arrived_trips()])

            with open(self.trip_output_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=all_records[0].keys())
                writer.writeheader()
                writer.writerows(all_records)