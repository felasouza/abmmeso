

class SignalPlan:
    PROTECTED = 3
    PERMITTED = 2
    STOP_PERMIT = 1
    FORBIDDEN = 0

    def __init__(self, plan_id, cycle, offset, protected_intervals, permitted_intervals, stop_permit_intervals, **kwargs):
        self.plan_id = plan_id
        self.cycle = cycle
        self.offset = offset
        self.protected_intervals = protected_intervals
        self.permitted_intervals = permitted_intervals
        self.stop_permit_intervals = stop_permit_intervals

        for k,v in kwargs.items():
            setattr(self, k, v)
    

    def get_right_of_way(self, link_id, instant):
        instant = instant % self.cycle

        for interval in self.protected_intervals[link_id]:
            if interval[0] <= instant < interval[1]:
                return SignalPlan.PROTECTED

        for interval in self.permitted_intervals[link_id]:
            if interval[0] <= instant < interval[1]:
                return SignalPlan.PERMITTED

        for interval in self.stop_permit_intervals[link_id]:
            if interval[0] <= instant < interval[1]:
                return SignalPlan.STOP_PERMIT

        return SignalPlan.FORBIDDEN