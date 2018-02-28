

from v2g_model.charger import Charger
from v2g_model.commute import Trip, Commute, Location
from v2g_model.vehicle import Vehicle


class Driver(object):

    def __init__(self, params):

        # See if we can charge at home
        # home_power is zero if home charging is unavailable,
        # otherwise is equal to the maximum power flow of the charger given EVSE
        # and vehicle's onboard charging equipment.
        # We will make an assumption that a home L2 EVSE will meet or exceed
        # the vehicle's charging capability, up to params['max_home_240v_power'].
        # This value in the default config will be 9.6kW (240V * 40A)
        home_power = 0
        if random.random() <= params['charging']['home']['240V_penetration']:
            home_power = min(model['charger_power'], params['charging']['home']['240v_power'])
        elif random.random() <= params['charging']['home']['120V_penetration']:
            home_power = min(model['charger_power'], params['charging']['home']['120v_power'])

        self.home_charger = Charger(home_power)

        # This will determine the minimum estimated distance remaining that a
        # driver will tolerate. This is used to estimate available SOC for V2G.
        self.range_anxiety = 1.0 + random.gauss(params['driver']['mean_range_anxiety'], params['driver']['sd_range_anxiety'])
        self.trip_range_buffer = self.range_anxiety * params['driver']['minimum_range_buffer']
