from collections import defaultdict
import pandas as pd

def get_data(f, num_categories=5):
	data = defaultdict(list)
	for line in f:
		if line in '.\n':
			continue
		split = line.split(':')
		key = split[0]
		value = float(split[1])
		data[key].append(value)

	df = pd.DataFrame(data)
	df['curCar deltaDamage'] = df['curCar final_damage'] - df['curCar starting_damage']
	df['obstacleCarAhead deltaDamage'] = df['obstacleCarAhead final_damage'] - df['obstacleCarAhead starting_damage']

	df['totalDamage'] = df['curCar deltaDamage'] + df['obstacleCarAhead deltaDamage']
	df['scaledDamage'] = df['totalDamage'] / 100
	df['speedDifference'] = df['curCar starting_speed'] - df['obstacleCarAhead starting_speed']
	df['collision'] = (df['curCar deltaDamage'] > 0) & (df['obstacleCarAhead deltaDamage'] > 0)

	df['discretizedBrakes'] = [round(num*(num_categories/10.0), 1)/(num_categories/10.0) for num in df['useBrakes']]
	df['discretizedSteering'] = [round(num*(num_categories/10.0), 1)/(num_categories/10.0) for num in df['useSteering']]

	df['collisionOrOffroad'] = df['collision'] | df['curCar went_offroad']
	df['collision_offroad'] = df['collision'] + 2*df['curCar went_offroad']
	df = df.replace({'collision_offroad': {0: 'None', 1: 'Collision', 2: 'Offroad', 3: 'Collision & Offroad'}})

	# df['collision'] = (df['curCar deltaDamage'] > 0)


	# remove negative starting distances
	df['starting_distance'] = df['starting_distance'].where(df['starting_distance'] > 0, float('NaN'))
	df['starting_distance'] = df['starting_distance'].where(df['starting_distance'] < 1000, float('NaN'))

	df = df.dropna()
	training = df[df['Training'] == 1]
	testing = df[df['Training'] == 0]
	return training, testing

EXAMPLE_MULTICAR_DATA = {'obstacleCarAhead starting_speed': 32.2902,
	'curCar starting_toMiddle': 0.0263338,
	'obstacleCarLeft starting_speed': 0.0121755,
	'obstacleCarRight starting_speed': 56.5245,
	'curCar starting_speed': 31.8883,
	'obstacleCarAhead starting_distance': -4.69141,
	'obstacleCarLeft starting_distance': 91.7539,
	'obstacleCarRight starting_distance': 56.6138,
	'useBrakes': 0.119679,
	'useSteering': 0.124236,
	'desiredLane': -1,
	'obstacleCarAhead starting_damage': 4987,
	'obstacleCarLeft starting_damage': 0,
	'obstacleCarRight starting_damage': 0,
	'curCar starting_damage': 3321,
	'obstacleCarAhead final_damage': 4987,
	'obstacleCarLeft final_damage': 0,
	'obstacleCarRight final_damage': 0,
	'curCar final_damage': 3321,
	'obstacleCarAhead final_speed': 0.00647697,
	'obstacleCarLeft final_speed': 0.00687902,
	'obstacleCarRight final_speed': 0.00636338,
	'curCar final_speed': 8.39855,
	'final_distance_obstacleCarAhead': -132.799,
	'final_distance_obstacleCarLeft': -76.2231,
	'final_distance_obstacleCarRight': -0.0203857,
	'curCar went_offroad': 0,
	'curCar maxAccel': 15.024,
	'curCar avgAccel': 2.71321}

MULTICAR_X_COLS = ['curCar starting_speed', 'obstacleCarLeft starting_distance',
				   'obstacleCarAhead starting_distance', 'obstacleCarRight starting_distance', 'curCar starting_toMiddle',
				   'discretizedBrakes', 'discretizedSteering', 'desiredLane']
def get_multicar_data(f, num_categories=5):
	
	data = defaultdict(list)
	for line in f:
		if line in '.\n':
			continue
		split = line.split(':')
		key = split[0]
		value = float(split[1])
		data[key].append(value)

	df = pd.DataFrame(data)

	# DELTA DAMAGE
	df['curCar deltaDamage'] = df['curCar final_damage'] - df['curCar starting_damage']
	df['obstacleCarAhead deltaDamage'] = df['obstacleCarAhead final_damage'] - df['obstacleCarAhead starting_damage']
	df['obstacleCarLeft deltaDamage'] = df['obstacleCarLeft final_damage'] - df['obstacleCarLeft starting_damage']
	df['obstacleCarRight deltaDamage'] = df['obstacleCarRight final_damage'] - df['obstacleCarRight starting_damage']

	df['totalDamage'] = df['curCar deltaDamage'] + df['obstacleCarAhead deltaDamage'] + df['obstacleCarLeft deltaDamage'] + df['obstacleCarRight deltaDamage']
	df['scaledDamage'] = df['totalDamage'] / 100

	# STARTING SPEED DIFFERENCE
	df['obstacleCarAhead speedDifference'] = df['curCar starting_speed'] - df['obstacleCarAhead starting_speed']
	df['obstacleCarLeft speedDifference'] = df['curCar starting_speed'] - df['obstacleCarLeft starting_speed']
	df['obstacleCarRight speedDifference'] = df['curCar starting_speed'] - df['obstacleCarRight starting_speed']

	# COLLISION
	df['obstacleCarAhead collision'] = (df['curCar deltaDamage'] > 0) & (df['obstacleCarAhead deltaDamage'] > 0)
	df['obstacleCarLeft collision'] = (df['curCar deltaDamage'] > 0) & (df['obstacleCarLeft deltaDamage'] > 0)
	df['obstacleCarRight collision'] = (df['curCar deltaDamage'] > 0) & (df['obstacleCarRight deltaDamage'] > 0)
	df['collision'] = df['obstacleCarAhead collision'] | df['obstacleCarLeft collision'] | df['obstacleCarRight collision'] 

	# DISCRETIZATION OF BRAKES/STEERING
	df['discretizedBrakes'] = [round(num*(num_categories/10.0), 1)/(num_categories/10.0) for num in df['useBrakes']]
	df['discretizedSteering'] = [round(num*(num_categories/10.0), 1)/(num_categories/10.0) for num in df['useSteering']]

	# COLLISION & OFFROAD
	df['collisionOrOffroad'] = df['collision'] | df['curCar went_offroad']
	df['collision_offroad'] = df['collision'] + 2*df['curCar went_offroad']
	df = df.replace({'collision_offroad': {0: 'None', 1: 'Collision', 2: 'Offroad', 3: 'Collision & Offroad'}})


	# remove negative and absurd starting distances
	df['obstacleCarAhead starting_distance'] = df['obstacleCarAhead starting_distance'].where(df['obstacleCarAhead starting_distance'] > 0, float('NaN'))
	df['obstacleCarAhead starting_distance'] = df['obstacleCarAhead starting_distance'].where(df['obstacleCarAhead starting_distance'] < 1000, float('NaN'))

	# remove NA's and split into training/testing
	df = df.dropna()
	training = df[df['Training'] == 1]
	testing = df[df['Training'] == 0]
	return training, testing