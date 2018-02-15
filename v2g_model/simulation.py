import random, datetime

def compute_weekday_interval_energy(vehicles, params, date, sunrise_time, sunset_time, interval):

    energy_demand = 0
    dispatchable_capacity = 0
    vehicles_plugged_in = 0
