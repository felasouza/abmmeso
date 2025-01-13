from .baseNode import BaseNode


class MergeNode(BaseNode):
    def __init__(self, node_id, inbound_links, outbound_link, priorities=None):
        self.node_id = node_id
        self.inbound_links = inbound_links
        self.outbound_link = outbound_link
        self.total_time = None
        self.time_step = None
        self.total_steps = None
        self.priorities = priorities
        # self.total_capacity = sum([link.cap for link in self.inbound_links])
        if len(self.inbound_links) != 2 and self.priorities is not None:
            raise ValueError("No priority can be defined for more than 2 inbound links")

    def start(self, time_step, total_time):
        self.time_step = time_step
        self.total_time = total_time
        self.total_steps = int(total_time / time_step)

    def prepare_step(self, t):
        pass

    def compute_flows(self, t):
        if len(self.inbound_links) == 2:
            self.compute_flows_as_two_inbounds(t)
        else:
            self.compute_flows_as_n_inbounds(t)

    def compute_flows_as_n_inbounds(self, t):
        demands = [link.get_demand() for link in self.inbound_links]
        supply = self.outbound_link.get_supply()

        demand_sum = sum(demands)
        flows_set = [None for _ in demands]

        if demand_sum <= supply:
            for i, link in enumerate(self.inbound_links):
                flows_set[i] = demands[i]
        else:
            set_flow_regardless = False
            while True:
                prevailing_capacity = 0
                for i, link in enumerate(self.inbound_links):
                    if flows_set[i] is None:
                        prevailing_capacity += link.get_capacity()

                shares = []
                for i, link in enumerate(self.inbound_links):
                    if flows_set[i] is None:
                        shares.append(link.get_capacity() / prevailing_capacity)
                    else:
                        shares.append(0)

                fair_shares = [share * supply for share in shares]

                flow_had_been_set = False
                for i, link in enumerate(self.inbound_links):
                    if flows_set[i] is None:
                        if demands[i] < fair_shares[i]:
                            flows_set[i] = demands[i]
                            flow_had_been_set = True

                if set_flow_regardless:
                    for i, link in enumerate(self.inbound_links):
                        if flows_set[i] is None:
                            flows_set[i] = fair_shares[i]
                            flow_had_been_set = True

                    break

                if flow_had_been_set == False:
                    set_flow_regardless = True

        for i, link in enumerate(self.inbound_links):
            link.set_outflow(flows_set[i])
        self.outbound_link.set_inflow(sum(flows_set))

    def compute_flows_as_two_inbounds(self, t):

        outbound_supply = self.outbound_link.get_supply()

        d0 = self.inbound_links[0].get_demand()
        d1 = self.inbound_links[1].get_demand()

        total_flow = 0

        g0 = min(d0, max(outbound_supply - d1, outbound_supply * self.priorities[0]))
        g1 = min(d1, max(outbound_supply - d0, outbound_supply * self.priorities[1]))
        total_flow = g0 + g1

        self.inbound_links[0].set_outflow(g0)
        self.inbound_links[1].set_outflow(g1)
        self.outbound_link.set_inflow(total_flow)
