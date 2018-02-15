from __future__ import absolute_import
import datetime, uuid
import apache_beam as beam

import random

class Model(object):

    count = 1

    def __init__(self, info):
        self.name = info['name']
        self.battery_size = info['battery_size']
        self.factory_range = info['factory_range']
        self.charger_power = info['charger_power']
        self.v2g_capable = bool(info['v2g_capable'])
        self.dcfc_capable = bool(info['dcfc_capable'])
        self.id = self.__class__.count

        self.__class__.count += 1

    def info(self):
        return {
            'name': self.name,
            'model_id': self.id,
            'charger_power': self.charger_power,
            'factory_range': self.factory_range,
            'battery_size': self.battery_size,
            'v2g_capable': self.v2g_capable,
            'dcfc_capable': self.dcfc_capable
        }


def daily_vehicle_sales(total):
    """Return a randomly chosen list of n positive integers summing to total.
    Each such list is equally likely to occur."""

    dividers = sorted(random.sample(xrange(1, total), 364))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]

class Vehicle(object):

    count = 1

    def __init__(self, model, params):

            # Model name
            self.id = self.__class__.count
            self.__class__.count += 1

            self.model_name = model['name']
            self.model_id = model['id']

            # Battery capacity in kWh
            self.max_battery_capacity = model['battery_size']

            # Mean driving efficiency in [dist]/kWh.
            # This randomizes efficiency of driving behavior
            base_efficiency = model['factory_range']/model['battery_size']
            self.driving_efficiency = random.gauss(base_efficiency, params['driver']['sd_driving_efficiency'])

            # Commute distance
            self.commute_distance = random.gauss(
                params['trips']['commute']['mean_distance'],
                params['trips']['commute']['sd_distance']
            )
            self.commute_pct_hwy = random.gauss(
                params['trips']['commute']['mean_pct_hwy'],
                params['trips']['commute']['sd_pct_hwy']
            )
            self.commute_hwy_distance = self.commute_pct_hwy * self.commute_distance
            self.commute_city_distance = self.commute_distance - self.commute_hwy_distance
            if self.commute_city_distance < .5:
                self.commute_city_distance = .5
                self.commute_hwy_distance = self.commute_distance - .5


            # See if we can charge at home
            # home_power is zero if home charging is unavailable,
            # otherwise is equal to the maximum power flow of the charger given EVSE
            # and vehicle's onboard charging equipment.
            # We will make an assumption that a home L2 EVSE will meet or exceed
            # the vehicle's charging capability, up to params['max_home_240v_power'].
            # This value in the default config will be 9.6kW (240V * 40A)
            self.home_power = 0
            if random.random() <= params['charging']['home']['240V_penetration']:
                self.home_power = min(model['charger_power'], params['charging']['home']['240v_power'])
            elif random.random() <= params['charging']['home']['120V_penetration']:
                self.home_power = min(model['charger_power'], params['charging']['home']['120v_power'])


            # work_power is similar to home_power, only for work. We assume 240V
            # supply voltage here, so no need for 120V.
            # We will have to calculate the probability that someone will be able to
            # charge at work on a daily basis (simulating charger congestion),
            # so we have to store these probabilities for each vehicle.
            # 240V will be preferred, so 120V probability is used as a fallback since
            # drivers should want to charge even if it is 120V.
            self.work_240v_power = 0
            self.work_120v_power = 0
            # First, figure out if work charging is even available.
            if random.random() <= params['charging']['work']['240V_penetration']:
                self.work_240v_power = min(model['charger_power'], params['charging']['work']['240v_power'])
            if random.random() <= params['charging']['work']['120V_penetration']:
                self.work_120v_power = min(model['charger_power'], params['charging']['work']['120v_power'])

            self.work_240v_availability = random.gauss(
                params['charging']['work']['mean_240V_availability'],
                params['charging']['work']['sd_240V_availability']
            )
            self.work_120v_availability = random.gauss(
                params['charging']['work']['mean_120V_availability'],
                params['charging']['work']['sd_120V_availability']
            )

            # This will determine the minimum estimated distance remaining that a
            # driver will tolerate. This is used to estimate available SOC for V2G.
            self.range_anxiety = 1.0 + random.gauss(params['driver']['mean_range_anxiety'], params['driver']['sd_range_anxiety'])
            self.trip_range_buffer = self.range_anxiety * params['driver']['minimum_range_buffer']



            self.depart_offset = random.gauss(0, params['trips']['commute']['sd_leave_hour'])
            dep_s = params['trips']['commute']['mean_leave_time']
            time_parts = dep_s.split(':')
            self.commute_depart_hour = time_parts[0]
            self.commute_depart_minute = time_parts[1]

            self.time_at_work = random.gauss(
                params['trips']['commute']['mean_time_at'],
                params['trips']['commute']['sd_time_at']
            )

            # Init this to true, since we'll start at midnight
            self.pluggeed_in = True

            # return {
                # 'id': the_id,
                # 'model_name': model_name,
                # 'model_id': model_id,
                # 'battery_capacity': battery_capacity,
                # 'driving_efficiency': driving_efficiency,
                # 'commute_distance': commute_distance,
                # 'commute_hwy_distance': commute_hwy_distance,
                # 'commute_city_distance': commute_city_distance,
                # 'driving_efficiency': driving_efficiency,
                # 'base_efficiency': base_efficiency,
                # 'home_power': home_power,
                # 'work_240v_power': work_240v_power,
                # 'work_240v_availability': work_240v_availability,
                # 'work_120v_power': work_120v_power,
                # 'work_120v_availability': work_120v_availability,
                # 'trip_range_buffer': trip_range_buffer,
                # 'range_anxiety': range_anxiety,
                # 'commute_depart_time': commute_depart_time,
                # 'time_at_work': time_at_work
