

class Charger(object):

    def __init__(self, power):

        self.max_power = power
        self.operating_power = power
        self.start_time = 0
        self.end_time = 0
        self.energy_short_of_full = 0
        self.connected = False

        self.nrg_charged = 0
        self.nrg_discharged = 0

    def connect(self, current_time, vehicle_power, vehicle_energy, vehicle_max_energy):
        self.connected = True
        self.start_time = current_time
        self.operating_power = min(vehicle_power, self.max_power)
        self.energy_short_of_full = vehicle_max_energy - vehicle_energy

        time_to_full_hrs = self.energy_short_of_full / self.operating_power

        self.end_time = self.start_time + datetime.timedelta(minutes = time_to_full_hrs * 60)

    def operate_charge(self, vehicle, current_time, time_interval):
        if vehicle.soc() < 1:
            time_interval
