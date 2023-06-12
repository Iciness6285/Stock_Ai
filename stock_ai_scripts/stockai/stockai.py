#### packages #####
import pickle
import numpy as np
import matplotlib.pyplot as plt
import json
import urllib.request
import time
from datetime import datetime, timedelta
import pytz
from calendar import timegm
from path import data_path, script_path
from tensorflow import keras
print("Done loading libraries.")


#### required constants ####
global apitoken_pol
apitoken_pol = "YOUR_API_TOKEN"	# replace this with your own polygon_api token. The free version is not in real time. Code can be adjusted to yfinance-api if you want free real time data.

n_days_insgesamt = 6 			# includes 1 tradingday + 5 previous days
n_days_chosen	 = 3			# choose, how many days you want to include, including tradingday
n_data_points 	 = 6			# specifies what one datapoint contains, [O H L C V Time]. So if it is 1, only the open values will be trained with
n_time_frame 	 = 30			# selects the timeframe each datapoint has, minimum is 1min, although this leads to too much parameters


#### functions ####
def todatetime(t): # Converts unixsec to string
	a = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime((t)))
	return a

def tounix(t):	   # Converts string to unixsec
	a = timegm(time.strptime(t, "%Y-%m-%d"))
	return a

def return_time_deviation(date):	# returns the correct time deviation, based on edt/est
	datetime_time = datetime.strptime(date, '%Y-%m-%d')
	if bool(pytz.timezone('America/New_York').dst(datetime_time, is_dst=None)) == True:
		time_deviation = 4
	else:
		time_deviation = 5
	return time_deviation


def downloaddata_pol(name, date):
	nontradingdays = pickle.load(open(script_path+'/getandsorteod/get_data/non_trading_days.pkl', 'rb'))
	date = "20"+date
	endtime = tounix(date) + 20*3600+return_time_deviation(date)*3600-60
	n = 1
	while n != n_days_insgesamt:
		eventdate_dt = datetime.strptime(date, '%Y-%m-%d')
		eventdate_dt += timedelta(days=-1)
		date = datetime.strftime(eventdate_dt, '%Y-%m-%d')
		if date not in nontradingdays:
			n += 1
	starttime = tounix(date) + 4*3600+return_time_deviation(date)*3600
	multiplier, timespan, limit = 1, "minute", 50000
	requesturl = f"https://api.polygon.io/v2/aggs/ticker/{name}/range/{multiplier}/{timespan}/{starttime*1000}/{endtime*1000}?adjusted=true&sort=asc&limit={limit}&apiKey={apitoken_pol}"
	print(requesturl)
	with urllib.request.urlopen(requesturl) as url: 					# getdata
		data_request = json.load(url)["results"]
	for i in range(len(data_request)):
		data_request[i]["volume"] = data_request[i].pop("v")
		data_request[i]["open"] = data_request[i].pop("o")
		data_request[i]["high"] = data_request[i].pop("h")
		data_request[i]["low"] = data_request[i].pop("l")
		data_request[i]["close"] = data_request[i].pop("c")
		data_request[i]["timestamp"] = data_request[i].pop("t")
		data_request[i].pop('vw', None)
		data_request[i].pop('n', None)
		data_request[i]["timestamp"] = int(data_request[i]["timestamp"]/1000)
	return data_request	



def data_to_np(data_request, border, date, starttime, finishtime):
# when finishtime in future, then no factual result can be given
	finishtimestamp = tounix("20"+date) +int(finishtime[:2])*3600+return_time_deviation("20"+date)*3600
	if finishtimestamp > int(time.time()):
		infuture = True
	else:
		infuture = False

	filledupdata = []
	tradingdays, n, count = [], 0, 0
	time_deviation = return_time_deviation(todatetime(data_request[count]["timestamp"])[:10])
	eventdate = todatetime(data_request[-1]["timestamp"]-time_deviation*3600)[:10]
	while n != n_days_insgesamt:					# creates list of trading days
		time_deviation = return_time_deviation(todatetime(data_request[count]["timestamp"])[:10])
		currentday = todatetime(data_request[count]["timestamp"]-time_deviation*3600)[:10]
		if currentday!=eventdate:
			tradingdays.append(currentday)
			n += 1
			eventdate = currentday
		count += 1
	for x in range(n_days_insgesamt):							# creates empty_list with correct timestamps
		tradingday = tradingdays[x]
		firsttime = tounix(tradingday) + 4*3600+return_time_deviation(tradingday)*3600
		for c in range(960):
			filledupdata.append(firsttime+c*60)
	try:
		for x in range(len(data_request)):						# replace timestamps with existing data
			timestamp_index = filledupdata.index(data_request[x]["timestamp"])
			filledupdata[timestamp_index] = data_request[x]
		for x in range(len(filledupdata)):						# fills up missing entries
			if x == 0:
				# print("HIaghaihgiah")
				number = filledupdata.index(data_request[0])
				previous_entry = {"open": data_request[0]["open"], "high": data_request[0]["high"], "low": data_request[0]["low"], \
									 "close": data_request[0]["close"], "volume": 0, "timestamp": data_request[0]["timestamp"]-number*60-60}
			else:	
				previous_entry = filledupdata[x-1]
			if isinstance(filledupdata[x], int):
				# print(x,"haighiahgiaghaighaighaighaig")
				missing_entry = {"open": previous_entry["open"], "high": previous_entry["high"], "low": previous_entry["low"], \
									 "close": previous_entry["close"], "volume": 0, "timestamp": previous_entry["timestamp"]+60}
				filledupdata[x] = missing_entry
	except ValueError:
		print("error")

	cutdata = filledupdata
	attributes = ["open", "high", "low", "close", "volume", "timestamp"] # brings form into np.array(array(array(...)))
	tickerdata = []
	i = 0
	for x in range(len(cutdata)):
		tickvalues = []
		i+=1
		for c in range(6):
			tickvalues.append(cutdata[x][attributes[c]])
		tickerdata.append(np.array(tickvalues, np.float64))


	if infuture == False:												# gives pct outcome based on start- & finish-time
		startcounter  = (int(starttime[:2])-4)*60 + int(starttime[3:]) + (n_days_insgesamt-1)*960
		finishcounter = (int(finishtime[:2])-4)*60 + (n_days_insgesamt-1)*960
		pctchng = (tickerdata[finishcounter][3]/tickerdata[startcounter][0]-1)*100

		inputdata = tickerdata[:startcounter]							# cuts tickerdata down to inputdata based on starttime

		check = False													# classifies the pctchng to the right number
		for i in range(len(border)):
			if (border[i] > pctchng) & (check == False):
				output = i
				check = True
		if check == False:
			output = 9
	else:
		output = "None"
		inputdata = tickerdata[:startcounter]							# cuts tickerdata down to inputdata based on starttime

	opens, highs, lows, closes, volumes, timestamps = [], [], [], [], [], [] # creates list in order to perform calculations
	for x in range(len(inputdata)):
		opens.append(inputdata[x].flat[0])
		highs.append(inputdata[x].flat[1])
		lows.append(inputdata[x].flat[2])
		closes.append(inputdata[x].flat[3])
		volumes.append(inputdata[x].flat[4])
		timestamps.append(inputdata[x].flat[5])

	logscaling = True 													# enables/disables log-scaling of volume parameter
	if logscaling == True:												# scales volume down logarithmically to avoid big vol spikes
		volumes[:] = [x if x != 0 else 1 for x in volumes]
		volumes = np.log(np.array(volumes))
	maxv, minv 	   = max(highs), 	min(lows)
	maxvol, minvol = max(volumes), 	min(volumes)
	maxt, mint 	   = max(timestamps), min(timestamps)
	normd = []
	for x in range(len(inputdata)):										# normalizes data between 0 and 1
		tick = []
		tick.append(((opens[x]-minv)/(maxv-minv)))
		tick.append(((highs[x]-minv)/(maxv-minv)))
		tick.append(((lows[x]-minv)/(maxv-minv)))
		tick.append(((closes[x]-minv)/(maxv-minv)))
		tick.append(((volumes[x]-minvol)/(maxvol-minvol)))
		tick.append(((timestamps[x]-mint)/(maxt-mint)))
		normd.append(tick)
	tickerdata = np.array(normd)

	inputv = tickerdata[(n_days_insgesamt-n_days_chosen)*960:]			# cuts down to specified range n_days_chosen

	final_data = inputv
	openvals, max_values, min_values, closevals, volumevals, timev = [], [], [], [], [], []
	for i in range(int(len(final_data)/n_time_frame)):
		max_values.append(np.max(final_data[:,1][i*n_time_frame:i*n_time_frame+n_time_frame]))
		min_values.append(np.min(final_data[:,2][i*n_time_frame:i*n_time_frame+n_time_frame]))
		openvals.append(final_data[:,0][i*n_time_frame:i*n_time_frame+n_time_frame][0])
		closevals.append(final_data[:,3][i*n_time_frame:i*n_time_frame+n_time_frame][-1])
		volumevals.append(np.sum(final_data[:,4][i*n_time_frame:i*n_time_frame+n_time_frame]))
		timev.append(final_data[:,5][i*n_time_frame:i*n_time_frame+n_time_frame][-1])
	inputv = (np.transpose(np.array([openvals, max_values, min_values, closevals, volumevals, timev])))
	
	data = (inputv, output, opens)
	return data


def stockai(name, date, starttime="09:30", finishtime="16:00", n_borders=10):
	endtimes, predictions, maxpreds, minpreds = [], [], [], []
	for i in range(int(starttime[:2]), int(finishtime[:2])):
		endtimes.append(str(i+1))
	data_request = downloaddata_pol(name, date)
	print("Done downloading data.")
	borders = pickle.load(open(data_path+f'/getandsorteod/data_to_np/final_data_{starttime[:2]}_{starttime[3:]}_{n_borders}.pkl', 'rb'))
	for i in range(len(endtimes)):
		(inputv, outputv, opens) = data_to_np(data_request, borders[i], date, starttime, endtimes[i])

		model_path = data_path+f'/traintf/model_{starttime[:2]}_{starttime[3:]}-{str(endtimes[i])}_00'
		model = keras.models.load_model(model_path)
		prediction = model.predict(np.array([inputv]))	# make prediction
		predictions.append(prediction[0])
		maxpreds.append(prediction[0].argmax(axis=0))
		minpreds.append(prediction[0].argmin(axis=0))
		print("Done with "+str(round((i+1)/len(endtimes)*100,2))+"%.")

	if maxpreds[-1] == len(borders[-1]):
		print(f"Values is at {finishtime} estimated to be over {round(borders[len(endtimes)-1][maxpreds[-1]-1], 3)}%.")
	else:
		print(f"Values is at {finishtime} probably between {round(borders[len(endtimes)-1][maxpreds[-1]-1], 3)}% and {round(borders[len(endtimes)-1][maxpreds[-1]], 3)}%.")
	if outputv != "None":
		print(f"Values is at {finishtime} factually between {round(borders[len(endtimes)-1][outputv-1], 3)}% and {round(borders[len(endtimes)-1][outputv], 3)}%.")
	else:
		print("Value (change%) lies in the future.")

	openval = opens[-1]				# baseline for the pct changes
	fig, ax = plt.subplots()
	for i in range(len(endtimes)):	# adds all rectangles
		maxpredictionval = max(predictions[i])
		for x in range(10):
			x_pos = 60*int(endtimes[i])+4560
			x_len = 55

			if x == 0 or x == 9:
				y_len = 0.02*openval
			else:
				y_len = (borders[i][x]-borders[i][x-1])/100*openval

			if x == 0:
				y_pos = borders[i][0]/100*openval-y_len+openval
				plt.text(x_pos+20, y_pos-0.002*openval, f'{endtimes[i]}:00')
			else:
				y_pos = borders[i][x-1]/100*openval+openval

			colorval = predictions[i][x]/maxpredictionval
			color = (1.0, 1.0-colorval, 1.0-colorval)
			rectangle = plt.Rectangle((x_pos, y_pos), x_len, y_len, fc=color,ec="black")
			plt.gca().add_patch(rectangle)

	topct = lambda toval: toval/openval
	toval = lambda topct: topct/openval*100-100

	plt.plot(opens)
	ax2 = ax.secondary_yaxis("right", functions=(toval, topct))	# adds 2nd y-axis
	ax.set_ylabel("Preis in $")
	ax2.set_ylabel('Veränderung in %')
	plt.show()


# makes a prediction, where stockprice will likely be over the next few hours
# additional arguments include, startingtime, endtime, n_borders
# 		tickername, date
stockai("SIEN", "23-06-09")