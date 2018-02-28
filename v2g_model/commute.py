from __future__ import absolute_import
import datetime, random, time
from v2g_model.utils import str_time, td_gauss

class Location(enum):
    HOME = 0
    CITY = 1
    HIGHWAY = 2
    DESTINATION = 3
    STOP = 4
    OTHER = 5

class Trip(object):

    def __init__(self, distance, pct_hwy, hwy_speed, city_speed, minimum_city_distance = 0.5):
        self.distance = distance
        base_hwy_distance = pct_hwy * distance
        self.city_distance = min(distance - base_hwy_distance, minimum_city_distance)
        self.hwy_distance = distance - self.city_distance
        self.pct_hwy = self.hwy_distance / distance
        self.pct_city = self.city_distance / distance
        self.hwy_speed = hwy_speed
        self.city_speed = city_speed

    def arrival_time(self, departure_time):
        hwy_time = self.hwy_distance / self.hwy_speed
        city_time = self.city_distance / self.city_speed
        time_min = (hwy_time + city_time) * 60
        delta = datetime.timedelta(minutes = time_min)
        return departure_time + delta

    def energy_consumed(self, efficiency, hwy_efficiency = 0, city_efficiency = 0):
        hwy_eff = efficiency
        city_eff = efficiency
        if hwy_efficiency > 0:
            hwy_eff = hwy_efficiency
        if city_efficiency > 0:
            city_eff = city_efficiency

        hwy_nrg =  self.hwy_distance / hwy_eff
        city_nrg = self.city_distance / city_eff

        return hwy_nrg + city_nrg


class Commute(object):

    def __init__(self, vehicle_info, commute_info, charging_info, driver_info):

        distance = random.gauss(
            commute_info['mean_distance'],
            commute_info['sd_distance']
        )

        pct_hwy = random.gauss(
            commute_info['mean_pct_hwy'],
            commute_info['sd_pct_hwy']
        )




        # Mean driving efficiency in [dist]/kWh.
        # This randomizes efficiency of driving behavior
        base_efficiency = random.gauss(
            vehicle_info['factory_range']/vehicle_info['battery_size'],
            driver_info['sd_driving_efficiency']
        )

        self.hwy_speed = random.gauss(
            commute_info['mean_hwy_speed'],
            commute_info['sd_hwy_speed']
        )

        hwy_efficiency_offset = (commute_info['mean_hwy_speed'] - self.hwy_speed) * (self.hwy_distance / self.distance)


        self.city_speed = random.gauss(
            commute_info['mean_city_speed'],
            commute_info['sd_city_speed']
        )

        city_efficiency_offset = (commute_info['mean_city_speed'] - self.city_speed) * (self.city_distance / self.distance)

        self.city_efficiency = base_efficiency + city_efficiency_offset
        self.hwy_efficiency = base_efficiency + hwy_efficiency_offset
        self.avg_efficiency = (self.city_efficiency + self.hwy_efficiency) / 2

        self.city_drive_time = datetime.timedelta(hour=self.city_distance / self.city_speed)
        self.hwy_drive_time = datetime.timedelta(hour=self.chwy_distance / self.hwy_speed)

        self.charger_240v_available = False
        self.charger_120v_available = False

        self.charge_power_240v = 0
        self.charge_power_120v = 0
        # First, figure out if work charging is even available.
        if random.random() <= charging_info['240V_penetration']:
            self.charger_power_240v = min(vehicle_info['charger_power'], charging_info['240v_power'])
            self.charger_240v_available = True
        if random.random() <= charging_info['120V_penetration']:
            self.charger_power_120v = min(model['charger_power'], params['charging']['work']['120v_power'])
            self.charger_120v_available = True

        self.charger_availability_240v = random.gauss(
            charging_info['mean_240V_availability'],
            charging_info['sd_240V_availability']
        )
        self.charger_availability_120v = random.gauss(
            charging_info['mean_120V_availability'],
            charging_info['sd_120V_availability']
        )

        self.target_depart_time = str_time(coomute_info['mean_leave_time'])
        sd_depart_time = td_gauss(0, coomute_info['sd_leave_time'])
        self.target_depart_time = self.target_depart_time + sd_depart_time

        self.sd_depart_delay = commute_info['sd_leave_delay']

        self.depart_time = self.target_depart_time



    def departure_time(self):
        morning_depart_offset = td_gauss(0, sd_leave_time)
        self.depart_time = self.target_depart_time + morning_depart_offset
        return self.depart_time

    def
