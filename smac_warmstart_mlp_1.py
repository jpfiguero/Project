from __future__ import division
import pandas as pd
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
import numpy as np
import urllib
import scipy
import os

import pysmac
import pysmac.analyzer
import pysmac.utils

import sklearn.ensemble
import sklearn.datasets
import sklearn.cross_validation
from sklearn import metrics
from sknn.mlp import Classifier, Layer
from time import time

# Function to calculate the median
def median(data):
    data = sorted(data)
    n = len(data)
    if n%2 == 1:
        return data[n//2]
    else:
        i = n//2
        return (data[i - 1] + data[i])/2

start = time()
n_iter = 100          ## Number of evaluations (SMAC)
n_validations = 25    ## Number of Monte-Carlo Cross-Validations for each model's accuracy evaluated

# Dataset 1

url1 = "http://archive.ics.uci.edu/ml/machine-learning-databases/pima-indians-diabetes/pima-indians-diabetes.data"
dataset1 = np.loadtxt(urllib.urlopen(url1), delimiter=",")
X = dataset1[:,0:8]
Y = dataset1[:,8]

# We fit the MLP with the hyperparameters given and return the model's median accuracy from 25 trials
def mlp(number_layers, number_neurons_1, number_neurons_2, number_neurons_3, number_neurons_4, dropout_rate):

	layers = []
	number_neurons = []

	number_neurons.append(number_neurons_1)
	number_neurons.append(number_neurons_2)
	number_neurons.append(number_neurons_3)
	number_neurons.append(number_neurons_4)

	for i in np.arange(number_layers):
		layers.append(Layer("Sigmoid", units=number_neurons[i], dropout = dropout_rate))

	layers.append(Layer("Softmax",  units=2))

	scores = []

	for i in np.arange(n_validations):

		X_train, X_test, Y_train, Y_test = sklearn.cross_validation.train_test_split(X,Y, test_size=0.3, random_state=1)
	
		predictor = Classifier(
	    layers=layers,
	    learning_rate=0.001,
	    n_iter=25)

		predictor.fit(X_train, Y_train)

		scores.append(metrics.accuracy_score(Y_test, predictor.predict(X_test)))
	
	return -median(scores)

# We create the optimizer object
opt = pysmac.SMAC_optimizer( working_directory = './results/dataset1/smac_warm/' % os.environ, persistent_files=True, debug = False)

# Warmstart for Dataset #1 (optimum parameters from Dataset #10)
parameter_definition=dict(\
		number_layers = ("integer", [1,4], 1),
		number_neurons_1  =("integer", [10,1000], 764, 'log'),
		number_neurons_2  =("integer", [10,1000], 257, 'log'),
		number_neurons_3  =("integer", [10,1000], 65, 'log'),
		number_neurons_4  =("integer", [10,1000], 33, 'log'),
		dropout_rate =("real", [0,1],    0.021309613332489707),
		)

# We set some parameters for the optimizer
value, parameters = opt.minimize(mlp,
					n_iter, parameter_definition,	# number of evaluations
					num_runs = 2,					# number of independent SMAC runs
					seed = 2,						# random seed
					num_procs = 2,					# two cores
					mem_limit_function_mb=1000,		# Memory limit
					t_limit_function_s = 10000	    # Time limit in seconds
					)

# We print the best configuration found and its accuracy
print(('The highest accuracy found: %f'%(-value)))
print(('Parameter setting %s'%parameters))
print("Bayesian Optimization took %.2f seconds for %d evaluations" % ((time() - start), n_iter))





