import time
import itertools  

import zmq
import numpy as np

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression

from cleaner import get_multicar_data, MULTICAR_X_COLS

print 'GETTING DATA'
K = 5
f = open('data_bin/train_test_multicar_lr.txt')
train, test = get_multicar_data(f)
df = train

print 'FITTING MODEL'
x_cols = MULTICAR_X_COLS
y_col = 'collisionOrOffroad'
train_x = df[x_cols]
train_y = df[y_col]

rfc = RandomForestClassifier(n_estimators=100)
lr = LogisticRegression()
ada = AdaBoostClassifier()

clf = rfc
clf2 = ada
clf.fit(train_x, train_y)
clf2.fit(train_x, train_y)


print 'ESTABLISHING SERVER'

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
print 'WAITING FOR REQUESTS'

x = np.zeros((1,len(x_cols)))
# behaviors = [(0,0), (0,1), (1,0), (1,1)]
brakesBehaviors = sorted(set(df['discretizedBrakes']))
steeringBehaviors = sorted(set(df['discretizedSteering']))
desiredLaneChoices = set([-1,1])
# desiredLaneChoices = set([-1])
behaviors = list(itertools.product(brakesBehaviors, steeringBehaviors, desiredLaneChoices))

probs = np.zeros(len(behaviors))

request_size = len(x_cols) - len(behaviors[0])
x2 = np.array([(0, 0, 0, 0, beh[0], beh[1], beh[2]) for beh in behaviors])

while True:
	#  Wait for next request from client
	message = socket.recv()
	t0 = time.time()
	print("Received request: \"%s\"" % message)

	split = message.split()
	try:
		for i,num in enumerate(split):
			x2[:, i] = float(num)
	except (ValueError, IndexError) as e:
		print 'ERROR, incorrect request size'
		min_proba_behavior = behaviors[np.argmin(probs[:,1])]
		string_behavior = [str(num) for num in min_proba_behavior]
		result = ' '.join(string_behavior) + '\n'
		#  Send reply back to client
		socket.send(result)
		continue
	if np.any(np.isnan(x)):
		print 'ERROR, NaN'
		min_proba_behavior = behaviors[np.argmin(probs[:,1])]
		string_behavior = [str(num) for num in min_proba_behavior]
		result = ' '.join(string_behavior) + '\n'
		#  Send reply back to client
		socket.send(result)
		continue

	probs = clf.predict_proba(x2)
	probs2 = clf2.predict_proba(x2)
	probs += probs2
	min_proba_behavior = behaviors[np.argmin(probs[:,1])]

	print probs[:,1]
	print np.min(probs[:,1])
	print np.argmin(probs[:,1])

	string_behavior = [str(num) for num in min_proba_behavior]
	result = ' '.join(string_behavior) + '\n'
	print result

	#  Send reply back to client
	socket.send(result)
	print "Processed in %fms" % ((time.time() - t0)*1000)
