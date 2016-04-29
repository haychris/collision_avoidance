import sys
import matplotlib.pyplot as plt
import seaborn as sns
from cleaner import get_multicar_data

default = 'data_bin/test_summary_data.txt'
f = open(sys.argv[1])
train, test = get_multicar_data(f)
df = test
x_cols = ['curCar starting_speed', 'obstacleCarAhead starting_distance', 'discretizedBrakes', 'discretizedSteering']
# df['bad'] = df['collision'] + 2*df['curCar went_offroad']
# sns.stripplot(x='speedDifference', y='starting_distance', data=df, hue='collision')
# plt.scatter(df['speedDifference'], df['starting_distance'], c=df['bad'])
# sns.jointplot(x="speedDifference", y="starting_distance",  color='collision_offroad', hue_order=['None', 'Collision', 'Offroad', 'Collision & Offroad'],data=df)
# plt.show()



# g = sns.FacetGrid(df, hue='collision_offroad', hue_order=['None', 'Collision', 'Offroad', 'Collision & Offroad'])
# g.map(plt.scatter, 'obstacleCarAhead speedDifference', 'obstacleCarAhead starting_distance')
# g.add_legend()
# plt.show()


total = len(df)
print round(1.0*sum(df['collision']) / total, 4),
print round(1.0*sum(df['curCar went_offroad'])/total, 4),
print round(1.0* sum(df['collisionOrOffroad'])/total, 4)