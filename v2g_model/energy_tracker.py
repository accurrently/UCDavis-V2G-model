
class EnergyTracker(object):

    def __init__(self):
        self.data = {}

    def new_interval(self, dtime):
        self.data[dtime.strftime('%Y-%m-%d %H:%M:%S')] = {
            'load': 0,
            'connected_vehicles': 0
        }
