import statistics as stat
import math as mt
import numpy as np
import random
from tqdm import tqdm
import logging

REGION = "Los Angeles County"
TOTAL_VEHICLES = 1000000000000000
BEV_SHARE_OF_VEHICLES = .005

BATTERY_ANNUAL_DEGRADE_RATE = .05
EARLY_RETIREMENT_RATE = .00005

AVG_DIST_TO_WORK = 15.0
SD_DIST_TO_WORK = 5.0

VEHICLE_CLASSES = [
	{"name": "Short Range BEV", "battery_size": 40.0, "range_mi": 107.0, "growth": -.1, "new_share": .5, "initial_year": 0, "mean_life": 8, "eol": 10},
	{"name": "Medium Range BEV", "battery_size": 60.0, "range_mi": 150.0, "growth": .1, "new_share": .3, "initial_year": 0, "mean_life": 8, "eol": 10},
	{"name": "Long Range BEV", "battery_size": 80.0, "range_mi": 238.0, "growth": .2, "new_share": .2, "initial_year": 0, "mean_life": 8, "eol": 10}
]

HOME_L2_CHARGING_AVAILABILITY = .5
HOME_L2_CHARGING_POWER = 6
HOME_L1_CHARGING_POWER = 1.4

WORK_CHARGING_AVAILABILITY = .1
WORK_CHARGING_POWER = 7.7

CURRENT_SERVICABLE_VEHICLES = []

def home_charging_power(l1_power, l2_power, l2_probability):
	x = np.random.binomial(1,l2_probability,1)
	if x >= 1:
		return l2_power
	return l1_power

def work_charging_power(l2_power, l2_probability):
	return home_charging_power(0, l2_power, l2_probability)

def get_efficiency(battery_kwh, range_mi):
	return range_mi / battery_kwh

def new_vehicles_for_year(year, current_v, vclasses = VEHICLE_CLASSES, initial_ev_pop = TOTAL_VEHICLES * BEV_SHARE_OF_VEHICLES):
	new_v = {}

	if year == 0:
		for cl in vclasses:
		if cl["initial_year"] == 0:
			new_v[cl["name"]] = int(cl["new_share"] * initial_ev_pop)
		return new_v

	old_count_v = 0
	for v in current_v:
		old_count += v["count"]

	new_count = 0
	for cl in vclasses:
		if (cl["initial_year"] < year <= cl["eol"]) and (cl["name"] in current_v):
			new_count += int(current_v[cl["name"]] * cl["growth"])


	# Process vehicles just starting production
	remaining_count = new_count
	for cl in vclasses:
		if cl["initial_year"] == year:
			n = int(new_count * cl["new_share"])
			new_v[cl["name"]] = n
			remaining_count -= n

	# process growth of remaining cars
	for cl in vclasses:
		if (cl["initial_year"] < year <= cl["eol"]):
			n = int(remaining_count * ((current_v[cl["name"]] * cl["growth"]) / new_count))
			new_v[cl["name"]] = current_v[cl["name"]] + n

	return new_v

def count_dead_vehicles(vehicles, vclasses = VEHICLE_CLASSES):
	new_v = {}
	for vc in vclasses:
		new_v[vc["name"]] = 0
	for v in vehicles:
		if v["retired"] and any(vc["name"] == v["class"] for vc in vclasses) :
			new_v[v["class"]] += 1
	return new_v

def remove_dead_vehicles(vehicles):
	x = []
	i = 0
	for v in vehicles:
		if not v["retired"]:
			x.append(v)
		else:
			i++
	logging.info("Removed {} retired vehicles".format(i))
	return x

def net_growth(current_v, new_v, retired_v, vclasses = VEHICLE_CLASSES):
	net_g = {}
	for vc in vclasses:
		if not vc["name"] in net_g:
				net_g[vc["name"]] = 0
		current = 0
		new = 0
		retired = 0
		if vc["name"] in current_v:
			current = current_v[vc["name"]]
		if vc["name"] in new_v:
			new = new_v[vc["name"]]
		if vc["name"] in current_v:
			retired = retired_v[vc["name"]]
		net_g[vc["name"]] = vc["growth"]
		net_g[vc["name"]] = float((new - retired) / current)





	
