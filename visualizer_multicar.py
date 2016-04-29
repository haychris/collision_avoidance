import matplotlib.pyplot as plt
import seaborn as sns
from cleaner import get_multicar_data

f = open('data_bin/train_test_multicar.txt')
train, test = get_multicar_data(f)
df = train
def facet_plot():
	x_cols = ['curCar starting_speed', 'starting_distance', 'discretizedBrakes', 'discretizedSteering']
	# df['bad'] = df['collision'] + 2*df['curCar went_offroad']
	g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collision_offroad', hue_order=['None', 'Collision', 'Offroad', 'Collision & Offroad'])
	g.map(plt.scatter,  'obstacleCarAhead speedDifference', 'obstacleCarAhead starting_distance')
	g.add_legend()
	plt.show()

# facet_plot()


def subset(dat, brake, steer):
	dat2 = dat[dat['discretizedBrakes']==brake]
	dat2 = dat2[dat2['discretizedSteering']==steer]
	return dat2

def statm(brake,steer):
	total = len(subset(df, brake, steer))
	percent_collision = 1.0*sum(subset(df, brake,steer)['collision']) / total
	percent_offroad = 1.0*sum(subset(df, brake,steer)['curCar went_offroad'])/total
	percent_both = 1.0* sum(subset(df, brake,steer)['collisionOrOffroad'])/total
	return percent_collision, percent_offroad, percent_both
discretizations = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
print '\\% Brake & \\% Steering & \\%Collisions & \\% Offroad &\\% Collision \\& Offroad \\\\'
for brake in discretizations:
	for steer in discretizations:
		percent_collision, percent_offroad, percent_both = statm(brake, steer)
		print round(brake,4), '&',
		print round(steer,4), '&',
		print round(percent_collision,4), '&',
		print round(percent_offroad,4), '&',
		print round(percent_both,4), '\\\\'


# statm(0.0,1.0)
# statm(1.0,0.0)
# statm(1.0,0.2)

# g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collision')
# g.map(plt.scatter, 'speedDifference', 'starting_distance')
# g.add_legend()
# plt.show()


# g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='curCar went_offroad')
# g.map(plt.scatter, 'curCar starting_speed', 'starting_distance')
# g.add_legend()
# plt.show()


# g = sns.FacetGrid(df, col='discretizedBrakes', row='discretizedSteering', hue='collisionOrOffroad')
# g.map(plt.scatter, 'curCar starting_speed', 'starting_distance')
# g.add_legend()
# plt.show()