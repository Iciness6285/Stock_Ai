#### packages #####
from path import data_path
import pickle
import numpy as np
from tensorflow import keras
import matplotlib.pyplot as plt
print("Done loading libraries.")

#### Hyperparameters ####
n_days_insgesamt = 6 			# includes 1 tradingday + 5 previous days
n_days_chosen	 = 3			# choose, how many days you want to include, including tradingday
n_data_points 	 = 6			# specifies what one datapoint contains, [O H L C V Time]. So if it is 1, only the open values will be trained with
n_time_frame 	 = 30			# selects the timeframe each datapoint has, minimum is 1min, although this leads to too much parameters

n_hidden = 1040
epochs   = 150
mbs 	 = 30
learning_rate = 0.001
validation_split=0.2


#### main functions ####
def train_model(inputv, outputv, starttime, endtime, n_borders, save=False):
	length = len(inputv[0])
	model = keras.models.Sequential()
	

	### layers ###
	model.add(keras.layers.Flatten(input_shape=(length, n_data_points)))
	model.add(keras.layers.Dense(n_hidden, activation='elu'))
	model.add(keras.layers.Dense(64, kernel_regularizer=keras.regularizers.l1(0.01), activation='relu'))
	model.add(keras.layers.Dense(n_borders, activation='softmax'))																		# final classication layer
	print(model.summary())

	model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])										# optimizer for the model
	model.optimizer.lr = learning_rate																									# sets the learningrate
	history = model.fit(inputv, outputv, validation_split=validation_split, epochs=epochs, batch_size=mbs, shuffle=True, verbose=2)		# training the model

	if save==True:																														# saving the model
		model.save(data_path+f'/traintf/model_{starttime[:2]}_{starttime[3:]}-{str(endtime)}_00')
	plt.plot(history.history['val_accuracy'])
	plt.plot(history.history['accuracy'])
	plt.title('Model accuracy')
	plt.ylabel('Accuracy')
	plt.xlabel('Epoch')
	plt.legend(['Validation'], loc='upper left')
	plt.show()
	
	import shutil
	import os
	val_acc = history.history['val_accuracy']

	window_size = 10
	highest_avg = float('-inf')
	for i in range(len(val_acc) - window_size + 1):
		window = val_acc[i:i+window_size]
		avg = sum(window) / window_size
		if avg > highest_avg:
			highest_avg = avg

	# automatically saves the script itself. The title of the saved file consists of the highest, and average valuation accuracy
	average_val_acc = round(sum(val_acc[-10:]) / len(val_acc[-10:]),5)
	backup_name = f'{ round(highest_avg,5)}%_avg_val_acc_{average_val_acc}%_val_acc.py'
	script_path = os.path.realpath(__file__)
	backup_dir = data_path+f'/traintf/'
	backup_path = os.path.join(backup_dir, backup_name)
	shutil.copy(script_path, backup_path)


def showdata(starttime):
	filename = data_path+f'/getandsorteod/data_to_np/final_data_{starttime[:2]}_{starttime[3:]}_10.pkl'
	file = open(filename, 'rb')
	borders = pickle.load(file)
	(inputdata, outputdata) = pickle.load(file)
	
	for x in range(len(inputdata)):
		vals = inputdata[x]
		val = []
		for i in range(len(vals)):
			val.append(vals[i][1])
		print(len(inputdata))
		print(len(val))
		print(val)
		plt.plot(val)
		plt.show()

# showdata("09:30")


def traintf(starttime, n_borders=10, train_hour="all", save=False):
	filename = data_path+f'/getandsorteod/data_to_np/final_data_{starttime[:2]}_{starttime[3:]}_{n_borders}.pkl'

	file = open(filename, 'rb')
	print("opened")
	borders = pickle.load(file)
	(inputdata, outputdata) = pickle.load(file)
	inputv = []
	for i in range(len(inputdata)):														# cutting inpudata down to specified n_days_chosen
		inputv.append(inputdata[i][(n_days_insgesamt-n_days_chosen)*960:])
	inputv = np.array(inputv)
	final_arr = []
	for x in range(len(inputv)):														# takes the 1min data and converts it to data with timeframes equal to n_time_frame
		if x%400 == 0:
			print(x/len(inputv))
		# print(x/len(inputv))
		tickerdata = inputv[x]
		openvals, max_values, min_values, closevals, volumevals, time = [], [], [], [], [], []
		for i in range(int(len(tickerdata)/n_time_frame)):
			max_values.append(np.max(tickerdata[:,1][i*n_time_frame:i*n_time_frame+n_time_frame]))
			min_values.append(np.min(tickerdata[:,2][i*n_time_frame:i*n_time_frame+n_time_frame]))
			openvals.append(tickerdata[:,0][i*n_time_frame:i*n_time_frame+n_time_frame][0])
			closevals.append(tickerdata[:,3][i*n_time_frame:i*n_time_frame+n_time_frame][-1])
			volumevals.append(np.sum(tickerdata[:,4][i*n_time_frame:i*n_time_frame+n_time_frame]))
			time.append(tickerdata[:,5][i*n_time_frame:i*n_time_frame+n_time_frame][-1])
		final_arr.append(np.transpose(np.array([openvals, max_values, min_values, closevals, volumevals, time])))
	inputv = np.array(final_arr)


	if train_hour=="all":
		endtimes = []
		for i in range(int(starttime[:2]), 16):											# creating endtimes
			endtimes.append(i+1)
		for i in range(len(endtimes)):													# train_model for each endtime
			outputv = outputdata[i]
			endtime = endtimes[i]
			train_model(inputv, outputv, starttime, endtime, n_borders,save=save)
	else:
		outputv = outputdata[train_hour-10]
		train_model(inputv, outputv, starttime, train_hour, n_borders, save=save)


# Trains an ML Model, with data ending at 09:30, and predicts the price at 16:00. 10 price ranges included.
# finishtime max val 16:00
traintf("09:30", n_borders=10, train_hour=16, save=True)