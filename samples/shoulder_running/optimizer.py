if __name__ == "__main__":
    import sys
    import os
    #os.chdir("../../")
    sys.path.append("../../")
    sys.path.append('.')

import numpy
import os
from ctm.ctmLink import CTMLink
from ctm.triangularFundamentalDiagram import TriangularFundamentalDiagram
from continuousSingleCommodity.originNode import OriginNode
from continuousSingleCommodity.destinationNode import DestinationNode
from continuousSingleCommodity.mergeNode import MergeNode
from continuousSingleCommodity.oneToOneNode import OneToOneNode
from continuousSingleCommodity.divergeNode import DivergeNode
from ctm.variableLaneFDLink import VariableLaneFDLink
import ctm.capacityDropMerge
import simulationengine.simulationRunner as simulationRunner
from scipy.optimize import differential_evolution

# Data
upstream= [121.2304423470158, 131.3879445175207, 135.36620840292113, 147.45343204965957, 121.96855327856917, 116.16250478700508, 170.86073021737548, 138.27887569206703, 156.53101265303403, 184.09347202749888, 190.074076876655, 135.50197445882515, 225.05358652631566, 194.52991745353805, 158.90927262654236, 184.29717564341465, 204.76265926366142, 175.2389901908838, 184.27778049257103, 184.29717564341465, 195.6074980569125, 176.10322413497852, 155.90927262654236, 165.06443383329128, 160.88987747569874, 179.40390350511237, 180.52027441017404, 174.3457180525815, 174.3457180525815, 158.05479078992727, 153.9772101865528, 165.09358109161448, 171.1905568458326, 159.01600048824002, 139.64749262221136, 166.66677870893935, 155.4728272005032, 180.78314961400105, 169.6279884072521, 175.80254476484467, 142.2400853903798, 165.6085932564085, 152.39524659712873, 136.43403689881595, 118.33706114460438, 115.61944056338409, 105.3564562954415, 113.16250478700533, 105.22069023953617, 108.29827084291065]
ramp_counts= [6, 7, 4, 7, 7, 4, 8, 5, 5, 5, 8, 7, 10, 8, 10, 8, 8, 17, 9, 10, 11, 11, 14, 17, 16, 23, 15, 21, 25, 27, 23, 25, 17, 31, 19, 11, 20, 29, 12, 25, 20, 17, 24, 20, 9, 16, 10, 11, 14, 10]

upstream = [el/120 for el in upstream]
ramp_counts = [el/120 for el in ramp_counts]

CONTROL_STEP = 300

def get_base_fd():
    return TriangularFundamentalDiagram(vf=30.0, w=6.6, kj=0.105)

def get_modified_fd():
    base_fd = get_base_fd()
    return TriangularFundamentalDiagram(vf=base_fd.vf * 2/3.0, w=base_fd.w, kj=base_fd.kj * (4/3))

def get_network_with_demands():
    fd = get_base_fd()
    inbound_link_upstream = CTMLink(link_id=1, length=1200, lm=30, fundamental_diagram=fd, num_lanes=3)
    inbound_link_1 = VariableLaneFDLink(link_id=2, length=300, kj=0.1, lm=30, fundamental_diagram=fd, num_lanes=3, alpha_d=0.0, alpha_r=0.0)
    inbound_link_2 = CTMLink(link_id=10, length=300, lm=30, fundamental_diagram=fd, num_lanes=1)
    outbound_link = VariableLaneFDLink(link_id=3, length=300, lm=30, fundamental_diagram=fd, num_lanes=3, alpha_d=0.3, alpha_r=0.0)
    outbound_link_further = CTMLink(link_id=4, length=300, lm=30, fundamental_diagram=fd, num_lanes=3, alpha_d=0.0)
    off_ramp_link = CTMLink(link_id=11, length=300, lm=30, fundamental_diagram=fd, num_lanes=1)


    origin_node_1 = OriginNode(1, inbound_link_upstream, upstream)
    origin_node_2 = OriginNode(2, inbound_link_2, ramp_counts)
    one_one_node = OneToOneNode(7, inbound_link_upstream, inbound_link_1)
    merge_node = ctm.capacityDropMerge.CapacityDropMergeNode(3, inbound_link_1, inbound_link_2, outbound_link, theta_l=0.0, theta_r=0.25)
    node_diverge = DivergeNode(4, outbound_link, [outbound_link_further, off_ramp_link], turn_rates = [0.85, 0.15])

    destination_node = DestinationNode(5, outbound_link_further)
    destination_node_off_ramp = DestinationNode(6, off_ramp_link)

    links = [inbound_link_1, inbound_link_2, outbound_link, outbound_link_further, off_ramp_link, inbound_link_upstream]
    nodes = [origin_node_1, origin_node_2, merge_node, node_diverge, destination_node, destination_node_off_ramp, one_one_node]
    
    runner = simulationRunner.SimulationRunner(links=links, nodes=nodes, time_step=1.0, total_time=6000)
    return runner

class ScheduleTransitionController:
    def __init__(self, link, schedule, control_step = CONTROL_STEP):
        self.link = link
        self.fd = get_base_fd()
        self.fd2 = get_modified_fd()
        self.schedule = schedule
        self.control_step = control_step
        self.control_actions = []
    
    def start(self, time_step, total_time):
        self.control_actions.append(False)

    def run_step(self, t):
        current = self.control_actions[-1]
        if t==0 or t % self.control_step != 0:
            return
        
        if t in self.schedule and current != self.schedule[t]:
            enable = self.schedule[t]
            self.link.set_switch(t, self.fd2 if enable else self.fd, self.link.num_lanes)
            current = enable
        
        self.control_actions.append(current)

def evaluate_control(schedule):
    runner = get_network_with_demands()
    
    controller_steps = runner.total_time / schedule.shape[0]
    current = False    
    schedule_by_switching_time = {}
    
    total_time_on = 0
    total_transitions = 0
    
    #penalty for the first and last time step to ensure starts and finish disabled
    if schedule[0] > 0.5:
        total_time_on += controller_steps*80
    
    
    if schedule[schedule.shape[0]-1] > 0.5:
        total_time_on += controller_steps*80
        total_transitions += 1

    
    for i in range(schedule.shape[0]):
        new = True if schedule[i] > 0.5 else False
        
        if new != current:
            schedule_by_switching_time[int(i * controller_steps)] = new
            total_transitions += 1
        current = new
        if current:
            total_time_on += controller_steps
    
    schedule_by_switching_time[0] = False
    controller = ScheduleTransitionController(runner.links[2], schedule_by_switching_time, CONTROL_STEP)
    runner.general_purpose_objects = [controller]
    runner.run()
    
    tts = 0
    for i in range(len(runner.links)):
        tts += runner.links[i].rho.flatten().sum()
    

    on_weight = 0.002
    transition_weight = 50
    
    return tts+ on_weight * total_time_on + transition_weight * total_transitions

def map_percentage_schedule_to_binary(percent_schedule):
    total_time = 6000
    control_steps = total_time//CONTROL_STEP
    schedule = numpy.zeros(control_steps)
    current_time = 0
    for i in range(int(percent_schedule.shape[0]/2)):
        time_on = current_time + percent_schedule[i*2]
        time_off = current_time + percent_schedule[i*2] + percent_schedule[i*2 + 1]
        step_on = int((time_on/100.0)*len(schedule))
        step_off = int((time_off/100.0)*len(schedule))
        current_time += percent_schedule[i*2] + percent_schedule[i*2 + 1]
        if step_off >= len(schedule):
            break
        
        for j in range(int(step_on), int(step_off)):
            schedule[j] = 1
            
    return schedule

def func_as_integer(schedule):
    return evaluate_try(map_percentage_schedule_to_binary(schedule))

def evaluate_try(schedule):
    try:
        return evaluate_control(schedule)
    except:
        return 1e7

def run_optimization(workers=None):
    if workers is None:
        workers = os.cpu_count()
    bounds = [(0, 100) for _ in range(4)]
    def iteration_callback(xk, convergence=None, **kwargs):
       print("Current schedule:", xk,  map_percentage_schedule_to_binary(xk))
       return None
    result = differential_evolution(func_as_integer, bounds, maxiter=120, popsize=30, disp=True, polish=False, workers=workers, callback=iteration_callback)
    return map_percentage_schedule_to_binary(result.x)

if __name__ == "__main__":
    # import sys
    # import os
    # os.chdir("../../")
    # sys.path.append("../../")
    # sys.path.append('.')
    

    run_optimization()