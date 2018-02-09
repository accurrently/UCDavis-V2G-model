from __future__ import absolute_import
import datetime, uuid
import apache_beam as beam

import random


def create_vehicle(id, model, params):

        # Model name
        model_name = model['name']
        model_id = model['id']

        # Battery capacity in kWh
        battery_capacity = model['battery_capacity']

        # Mean driving efficiency in [dist]/kWh.
        # This randomizes efficiency of driving behavior
        base_efficiency = model['max-range_new']/model['battery_capacity']
        driving_efficiency = random.gauss(base_efficiency, params['stdev_driving_efficiency'])

        # Commute distance
        commute_distance = random.gauss(params['mean_commute_distance'], params['stdev_commute_distance'])

        # See if we can charge at home
        # home_power is zero if home charging is unavailable,
        # otherwise is equal to the maximum power flow of the charger given EVSE
        # and vehicle's onboard charging equipment.
        # We will make an assumption that a home L2 EVSE will meet or exceed
        # the vehicle's charging capability, up to params['max_home_240v_power'].
        # This value in the default config will be 9.6kW (240V * 40A)
        home_power = 0
        if random.random() <= params['home_240v_charger_penetration']:
            home_power = model['charger_power']
            if home_power >= params['max_home_240v_power']:
                home_power = params['max_home_240v_power']
        elif random.random() <= params['home_120v_charger_penetration']:
            home_power = params['max_home_120v_power']
        
