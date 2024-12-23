from continuous.link import Link
from continuous.mergeNode import MergeNode
from continuous.originNode import OriginNode
from continuous.destinationNode import DestinationNode
from continuous.oneToOneNode import OneToOneNode
from simulationengine.simulationRunner import SimulationRunner

import discrete.link
import discrete.originNode
import discrete.destinationNode
import discrete.oneToOneNode
import discrete.mergeNode
from demand.trip import Trip

import pickle

def load_data():
    data_source = "C:\\users\\fdesouza\\Downloads\\data_v7.pickle"
    with open(data_source, 'rb') as f:
        data = pickle.load(f)
    
    #print(data.keys(), data['data'].keys(), data['data'][2017,8,16].keys(), data['time_from'], data['time_to'], data['sample_time'])

    upstream_demands = [el/120 for el in data['data'][2017,8,16]['updemand']]
    ramp_demands = [el/120 for el in data['data'][2017,8,16]['ramp_counts']]
    downstream_flow = [el/120 for el in data['data'][2017,8,16]['down_count']]
    return upstream_demands, ramp_demands, data['data'][2017,8,16]['up_density'], downstream_flow

up, ramp, density, downstream_flow = load_data()
data = {'upstream': up, 'ramp': ramp, 'upstream_density': density, 'downstream_flow': downstream_flow}

def group_data(data, group_size):
    return [sum(data[i:i+group_size])/group_size for i in range(0, len(data), group_size)]


def run_for_parameters(args):
    vf, w, kj = args
    runner = run_scenario(vf, w, kj)

    nv_link = [(runner.links[1].cumulative_inflows[i] - runner.links[1].cumulative_outflows[i])/runner.links[1].length for i in range(len(runner.links[1].cumulative_inflows))]
    grouped_nv = group_data(nv_link, 600)
    grouped_from_data = group_data(data['upstream_density'], 5)
    
    norm_2_error = sum([(grouped_nv[i]-grouped_from_data[i])**2 for i in range(len(grouped_nv)-1)])
    return norm_2_error


def run_scenario(vf, w, kj):
    upstream_link = Link(link_id=1, length=900, vf=vf, w=w, kj=3*kj)
    transition_link = Link(link_id=2, length=150, vf=vf, w=w, kj=3*kj)
    ramp_link = Link(link_id=3, length=300, vf=vf, w=w, kj=kj)
    downstream_link = Link(link_id=4, length=900, vf=vf, w=w, kj=3*kj)

    upstream_node = OriginNode(node_id=1, link=upstream_link, demands=data['upstream'])
    ramp_node = OriginNode(node_id=2, link=ramp_link, demands=data['ramp'])
    up_to_transition_node = OneToOneNode(node_id=3, inbound_link=upstream_link, outbound_link=transition_link)
    
    merge_node = MergeNode(node_id=4, inbound_links=[transition_link, ramp_link], outbound_link=downstream_link, 
                           priorities = [0.75, 0.25])
    destination_node = DestinationNode(node_id=5, link=downstream_link)

    all_links = [upstream_link, transition_link, ramp_link, downstream_link]
    all_nodes = [upstream_node, ramp_node, up_to_transition_node, merge_node, destination_node]

    runner = SimulationRunner(links = all_links, nodes = all_nodes, time_step = 1.0, total_time=8*3600)
    runner.run()
    return runner

def run_scenario_discrete(vf, w, kj):
    upstream_link = discrete.link.Link(link_id=1, length=900, vf=vf, w=w, kj=3*kj)
    transition_link = discrete.link.Link(link_id=2, length=150, vf=vf, w=w, kj=3*kj)
    ramp_link = discrete.link.Link(link_id=3, length=300, vf=vf, w=w, kj=kj)
    downstream_link = discrete.link.Link(link_id=4, length=900, vf=vf, w=w, kj=3*kj)

    upstream_trips = Trip.from_continuous_demand(data['upstream'], 8*3600)
    ramp_trips = Trip.from_continuous_demand(data['ramp'], 8*3600)

    upstream_node = discrete.originNode.OriginNode(node_id=1, link=upstream_link, demand_trips=upstream_trips)
    ramp_node = discrete.originNode.OriginNode(node_id=2, link=ramp_link, demand_trips=ramp_trips)
    up_to_transition_node = discrete.oneToOneNode.OneToOneNode(node_id=3, inbound_link=upstream_link, outbound_link=transition_link)
    
    merge_node = discrete.mergeNode.MergeNode(node_id=4, inbound_links=[transition_link, ramp_link], outbound_link=downstream_link, 
                           priority_vector = [0,0,0,1,0,0,0,1])
    destination_node = discrete.destinationNode.DestinationNode(node_id=5, link=downstream_link)

    all_links = [upstream_link, transition_link, ramp_link, downstream_link]
    all_nodes = [upstream_node, ramp_node, up_to_transition_node, merge_node, destination_node]

    runner = SimulationRunner(links = all_links, nodes = all_nodes, time_step = 1.0, total_time=8*3600)
    runner.run()
    return runner

if __name__ == '__main__':
    import pylab
    import matplotlib
    
    import matplotlib
    matplotlib.rcParams.update(
        {
            'text.usetex': False,
            'font.family': 'stixgeneral',
            'mathtext.fontset': 'stix',
        }
    )


    runner = run_scenario(2.958e+01,  5.532e+00,  1.059e-01)
    runner_discrete = run_scenario_discrete(2.958e+01,  5.532e+00,  1.059e-01)

    f, axs = pylab.subplots(1,3, figsize=(9,4.5))


    nv_continuous = [(runner.links[1].cumulative_inflows[i] - runner.links[1].cumulative_outflows[i])/runner.links[1].length for i in range(len(runner.links[1].cumulative_inflows))]
    nv_discrete = [(runner_discrete.links[1].cumulative_inflows[i] - runner_discrete.links[1].cumulative_outflows[i])/runner_discrete.links[1].length for i in range(len(runner_discrete.links[1].cumulative_inflows))]
    
    vehicles_by_link_discrete = []
    vehicles_by_link_continuous = []
    for u in range(len(runner_discrete.links)):
        nv_link_continuous = [(runner.links[u].cumulative_inflows[i] - runner.links[u].cumulative_outflows[i]) for i in range(len(runner.links[u].cumulative_inflows))]
        nv_link_discrete = [(runner_discrete.links[u].cumulative_inflows[i] - runner_discrete.links[u].cumulative_outflows[i]) for i in range(len(runner_discrete.links[u].cumulative_inflows))]
        vehicles_by_link_continuous.append(nv_link_continuous)
        vehicles_by_link_discrete.append(nv_link_discrete)
    
    total_by_step_continuous = [sum([vehicles_by_link_continuous[u][i] for u in range(len(vehicles_by_link_continuous))]) for i in range(len(vehicles_by_link_continuous[0]))]
    total_by_step_discrete = [sum([vehicles_by_link_discrete[u][i] for u in range(len(vehicles_by_link_discrete))]) for i in range(len(vehicles_by_link_discrete[0]))]

    gs = 120
    time_step = (1/30.0)
    
    grouped_nv_continuous = group_data(nv_continuous, gs)
    grouped_nv_continuous[-1] = grouped_nv_continuous[-2]
    grouped_nv_discrete = group_data(nv_discrete, gs)
    grouped_nv_discrete[-1] = grouped_nv_discrete[-2]

    times_density = [4+time_step*i for i in range(len(grouped_nv_continuous))]
    

    downstream_flows_continuous = [runner.links[3].cumulative_outflows[i+1]-runner.links[3].cumulative_outflows[i] for i in range(len(runner.links[3].cumulative_outflows)-1)]
    downstream_flows_discrete = [runner_discrete.links[3].cumulative_outflows[i+1]-runner_discrete.links[3].cumulative_outflows[i] for i in range(len(runner_discrete.links[3].cumulative_outflows)-1)]
    grouped_flows_downstream = group_data(downstream_flows_continuous, gs)
    grouped_flows_downstream_discrete = group_data(downstream_flows_discrete, gs)

    ramp_flows_continuous = [runner.links[2].cumulative_outflows[i+1]-runner.links[2].cumulative_outflows[i] for i in range(len(runner.links[2].cumulative_outflows)-1)]
    ramp_flows_discrete = [runner_discrete.links[2].cumulative_outflows[i+1]-runner_discrete.links[2].cumulative_outflows[i] for i in range(len(runner_discrete.links[2].cumulative_outflows)-1)]

    transition_flows_continuous = [runner.links[1].cumulative_outflows[i+1]-runner.links[1].cumulative_outflows[i] for i in range(len(runner.links[1].cumulative_outflows)-1)]
    transition_flows_discrete = [runner_discrete.links[1].cumulative_outflows[i+1]-runner_discrete.links[1].cumulative_outflows[i] for i in range(len(runner_discrete.links[1].cumulative_outflows)-1)]


    grouped_data = group_data(data['upstream_density'], 1)
    grouped_data_flow = group_data(data['downstream_flow'], 1)

    times_flows = [4+time_step*i for i in range(len(grouped_flows_downstream))]
   
    axs[0].plot(times_density, grouped_nv_continuous, label='Continuous')
    axs[0].plot(times_density, grouped_nv_discrete, label='Discrete')
    axs[0].plot([4+time_step*i for i in range(len(grouped_data))], grouped_data, label='Data', color='black')
    axs[0].legend()

    axs[1].plot(times_flows, [el*3600 for el in grouped_flows_downstream], label='Continuous')
    axs[1].plot(times_flows, [el*3600 for el in grouped_flows_downstream_discrete], label='Discrete')
    axs[1].plot(times_flows, [el*3600 for el in group_data(ramp_flows_continuous, gs)],linestyle='--', label='Ramp')
    #axs[1].plot(group_data(ramp_flows_discrete, gs), label='D-R')
    #axs[1].plot(group_data(transition_flows_continuous, gs), label='C-T')
    #axs[1].plot(group_data(transition_flows_discrete, gs), label='D-T')
    axs[1].plot(times_flows, [el*3600 for el in grouped_data_flow], label='Data', color='black')
    axs[1].legend()
    axs[0].set_ylim(0, 0.15)
    axs[1].set_ylim(0, 6500)
    axs[2].set_ylim(0,200)
    axs[2].set_ylabel("Vehicles in the network (veh)")
    axs[0].set_xlim(4,12)
    axs[1].set_xlim(4,12)
    axs[2].set_xlim(4,12)
    axs[0].set_xlabel('Time of Day (h)')
    axs[1].set_xlabel('Time of Day (h)')
    axs[2].set_xlabel('Time of Day (h)')
    axs[0].grid(True)
    axs[1].grid(True)
    axs[2].grid(True)
    axs[0].set_ylabel('Density (veh/m)')
    axs[1].set_ylabel('Flow (veh/h)')
    axs[0].set_title('(a)')
    axs[1].set_title('(b)')
    axs[2].set_title('(c)')
    times_in_net = [4+(1.0*i)/3600 for i in range(len(total_by_step_continuous))]
    axs[2].plot(times_in_net, total_by_step_continuous, label='Continuous')
    axs[2].plot(times_in_net, total_by_step_discrete, label='Discrete')
    axs[2].legend()
    pylab.tight_layout()
    pylab.savefig("C:\\temp\\paper\\ltm_freeway_scenario.pdf", dpi=600)
    pylab.show()

    #print(run_for_parameters((30.0, 6.0, 1.0)))


    # f, axs = pylab.subplots(1, 3, figsize=(15, 5))


    # axs[0].plot(runner.get_times(1), runner.links[0].cumulative_outflows, label='Upstream Link')
    # axs[0].plot(runner.get_times(1), runner.links[1].cumulative_outflows, label='Transition Link')
    # axs[0].plot(runner.get_times(1), runner.links[2].cumulative_outflows, label='Ramp Link')
    # axs[0].plot(runner.get_times(1), runner.links[3].cumulative_outflows, label='Downstream Link')
    # axs[0].legend()

    # for index in range(4):
    #     nv_link = [(runner.links[index].cumulative_inflows[i] - runner.links[index].cumulative_outflows[i])/runner.links[index].length for i in range(len(runner.links[index].cumulative_inflows))]
    #     grouped_nv = group_data(nv_link, 120)
    #     flows = [runner.links[index].cumulative_outflows[i+1]-runner.links[index].cumulative_outflows[i] for i in range(len(runner.links[index].cumulative_outflows)-1)]
    #     axs[1].plot( grouped_nv, label=f'Link {index+1}')
    #     axs[2].plot(runner.get_times(), flows, label=f'Link {index+1}')
    # axs[1].legend()
    # axs[2].legend()
    # axs[1].plot(data['upstream_density'], label='Upstream Density', color='black')
    # pylab.tight_layout()
    # pylab.show()

    from scipy.optimize import differential_evolution

    bounds = [(20, 30.0), (4, 8), (0.05, 0.15)]
    #result = differential_evolution(run_for_parameters, bounds, disp=True, workers=4, maxiter=100)
    #print(result.x, result.fun)
    #print(result)