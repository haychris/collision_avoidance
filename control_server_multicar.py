import time
import itertools  

import zmq
import numpy as np

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sknn.mlp import Classifier, Layer, Regressor

from sklearn import preprocessing

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

norm = True

if norm:
	scaler = preprocessing.MinMaxScaler((-1,1))
	scaler.fit(train_x)
	train_x = scaler.transform(train_x)


rfc = RandomForestClassifier(n_estimators=100)
lr = LogisticRegression()
ada = AdaBoostClassifier()

max_layer_size = len(x_cols)**2
max_layers = [Layer("Sigmoid", units=max_layer_size/4),
			  Layer("Rectifier", units=max_layer_size/2),
			  Layer("Softmax")]
nn = Classifier(layers=max_layers,learning_rate=0.08, n_iter=300)

classifiers = [nn]
for clf in classifiers:
	clf.fit(train_x, train_y)
# clf = rfc
# clf2 = rfc
# clf.fit(train_x, train_y)
# clf2.fit(train_x, train_y)


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

	if norm:
		for i,beh in enumerate(behaviors):
			x2[i,4:] = beh
		x2 = scaler.transform(x2)
	probs = classifiers[0].predict_proba(x2)
	for clf in classifiers[1:]:
		probs += clf.predict_proba(x2)
	# probs = clf.predict_proba(x2)
	# probs2 = clf2.predict_proba(x2)
	# probs += probs2
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
