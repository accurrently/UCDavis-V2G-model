from __future__ import absolute_import
import datetime, time, uuid
#import apache_beam as beam

import random

from v2g_model.utils import td_gauss, td_minutes, str_time, str_timedelta
from v2g_model.




def daily_vehicle_sales(total):
    """Return a randomly chosen list of n positive integers summing to total.
    Each such list is equally likely to occur."""

    dividers = sorted(random.sample(xrange(1, total), 364))
    return [a - b for a, b in zip(dividers + [total], [0] + dividers)]






class Vehicle(object):

    class Status(enum):
        STOPPED = 0
        MOVING = 1

    count = 1

    def __init__(self, model, params):

        # Model name
        self.id = self.__class__.count
        self.__class__.count += 1

        self.model_name = model['name']
        self.model_id = model['id']

        # Battery capacity in kWh
        self.max_battery_energy = model['battery_size']
        self.battery_energy = self.max_battery_energy

        self.efficiency =  model['factory_range']/model['battery_size']

        # Init this to true, since we'll start at midnight
        self.plugged_in = True
        self.status = Vehicle.Status.STOPPED

    def charge(self, energy = 0):
        self.battery_energy = self.battery_energy + energy
        if self.battery_energy > self.max_battery_energy:
            self.battery_energy = self.max_battery_energy
        if self.battery_energy < 0:
            self.battery_energy = 0
        return self.battery_energy

    def soc(self):
        return self.battery_energy / self.max_battery_energy

    def degrade(self, percentage):
        self.max_battery_energy = self.max_battery_energy - (self.max_battery_energy * percentage)
        return self.max_battery_energy

    def maximum_range(self):
        return self.efficiency * self.max_battery_energy

    def range_current_soc(self):
        return self.efficiency * self.battery_energy

    def drive(self, distance, efficiency):
        discharge = (distance / efficiency) * -1
        return self.charge(energy = discharge)

    def excess_energy(self, energy_constraint, soc_constraint = 0.70):
        soc_nrg = min(self.max_battery_energy * soc_constraint, self.max_battery_energy - self.battery_energy)
        nrg_nrg = min(self.max_battery_energy - energy_constraint, self.max_battery_energy - self.battery_energy)

        return min(soc_nrg, nrg_nrg)

    def prepare_vehicle_for_day(self, params):

        # Battery degredation (linear for now)
        self.max_battery_capacity = self.max_battery_capacity - (self.max_battery_capacity * params['battery']['annual_degradation_rate'] / 365)

        # When the vehicle begins its commute, assume all dispatchable power
        # has been discharged overnight

        self.current_battery_capacity = self.minimum_commute_energy



        # Figure out what time the driver will depart in the morning
        morning_depart_offset = td_gauss(0, params['trips']['commute']['sd_daily_leave_time'])
        evening_depart_offset =  td_gauss(0, params['trips']['commute']['sd_daily_leave_time'])
        self.depart_for_work_time = self.base_depart_for_work_time + morning_depart_offset

        self.arrive_at_work_time = self.depart_for_work_time + self.city_commute_time + self.hwy_commute_time
        self.leave_work_time = self.arrive_at_work_time + self.time_at_work + evening_depart_offset

    def process_interval(self, day):

        SATURDAY = 5
        SUNDAY = 6
        # If a weekend, set energy to maximum, then do nothing (for now)
        # TODO: logic for weekend trips
        if day.weekday() == SATURDAY or day.weekday() == SUNDAY:
            # process weekends
            pass
        else:
            # Proess weekdays

class Model(object):

    count = 1

    def __init__(self, info):
        self.name = info['name']
        self.battery_size = info['battery_size']
        self.factory_range = info['factory_range']
        self.charger_power = info['charger_power']
        self.v2g_capable = bool(info['v2g_capable'])
        self.dcfc_capable = bool(info['dcfc_capable'])
        self.first_year = info['first_year']
        self.id = self.__class__.count
        self.__class__.count += 1

        self.daily_sales = []
        for yearly_sales in info['sales']
            dividers = sorted(random.sample(xrange(1, yearly_sales), 364))
            daily_numbers = [a - b for a, b in zip(dividers + [yearly_sales], [0] + dividers)]
            for day in daily_numbers:
                self.monthly_sales.append(day)

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

    def create_vehicle(self, params):
        return Vehicle(self.info, params)

    def create_vehicles_for_date(self, dtime):
        # TODO: match up supplied dtime with self.daily_sales[date_time] and
        # crete the appropriate number of vehicles
        pass
