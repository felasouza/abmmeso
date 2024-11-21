

class Trip:
    def __init__(self, **kwargs):
        self.trip_id = 0
        self.origin = 0
        self.destination = 0
        self.start = 0
        self.route = []
        self.end = None
        self.travel_times = []