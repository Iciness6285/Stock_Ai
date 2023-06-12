import numpy as np
from path import data_path
import pickle
n_days_insgesamt = 6


def data_to_np(starttime="09:30", n_borders=10, n_days_after=0):
### gives back the data till the starting time, the pct chng at each whole hour, the borders for each pct chng
### starttime:		  model has information until this time
### finishtime:		  model predicts the outcome at this time (%-chg from startt. to finisht.)

	cleaned_data = np.load(data_path+f'/getandsorteod/clean_data/cleaned_data_{n_days_after}.npy')
	# Creating borders & outputv #
	outputdata, borders, finishtime = [], [], []
	for i in range(int(starttime[:2]), 16):								# finishtimes & borders until 16:00 O'clock
		finishtime.append(i+1)

	for i in range(len(finishtime)):
		outputlist, borderlist = [], []
		pctchng = []
		for x in range(len(cleaned_data)):								# gives pct outcome based on start- & finish-time
			startcounter  = (int(starttime[:2])-4)*60 + int(starttime[3:]) + (n_days_insgesamt-1)*960
			finishcounter = (finishtime[i]-4)*60 + (n_days_insgesamt-1)*960
			pctchng.append((cleaned_data[x][finishcounter][3]/cleaned_data[x][startcounter][0]-1)*100)

		inputdata = []
		for x in range(len(cleaned_data)):								# cuts cleaned_data down to inputdata based on starttime
			inputdata.append(cleaned_data[x][:startcounter])

		sortedpcts = sorted(pctchng)									# creates normed outputdata, with 10 different classifications
		leninterv = int(((len(sortedpcts) - (n_borders-1))/n_borders))
		for x in range(n_borders-1): 				 					# creates borders for each time
			borderlist.append(sortedpcts[leninterv*(x+1)+x])
		print(borderlist)
		print(leninterv)
		print(len(cleaned_data))
		for x in range(len(pctchng)): 									# creates ouputlist
			count = 0
			try:
				while pctchng[x] > borderlist[count]:
					count += 1
				outputlist.append(count)
			except IndexError:
				outputlist.append(n_borders-1)

		borders.append(borderlist)		
		outputdata.append(outputlist)
		print(i/len(finishtime))
		print({i:outputlist.count(i) for i in outputlist})
	outputdata = np.array(outputdata)
	print("Done creating borders")

	# Normalizing #
	normeddata = []														# normalizes inputdata
	for i in range(len(inputdata)):										# creates list in order to perform calculations
		print(i/len(inputdata)*100)					
		opens, highs, lows, closes, volumes, timestamps = [], [], [], [], [], []
		for x in range(len(inputdata[i])):
			opens.append(inputdata[i][x].flat[0])
			highs.append(inputdata[i][x].flat[1])
			lows.append(inputdata[i][x].flat[2])
			closes.append(inputdata[i][x].flat[3])
			volumes.append(inputdata[i][x].flat[4])
			timestamps.append(inputdata[i][x].flat[5])
		logscaling = True 												# enables/disables log-scaling of volume parameter
		if logscaling == True:											# scales volume down logarithmically to avoid big vol spikes
			volumes[:] = [x if x != 0 else 1 for x in volumes]
			volumes = np.log(np.array(volumes))
		maxv, minv 	   = max(highs), 	min(lows)
		maxvol, minvol = max(volumes), 	min(volumes)
		maxt, mint 	   = max(timestamps), min(timestamps)
		normd = []
		for x in range(len(inputdata[i])):								# normalizes data between 0 and 1
			tick = []
			tick.append(((opens[x]-minv)/(maxv-minv)))
			tick.append(((highs[x]-minv)/(maxv-minv)))
			tick.append(((lows[x]-minv)/(maxv-minv)))
			tick.append(((closes[x]-minv)/(maxv-minv)))
			tick.append(((volumes[x]-minvol)/(maxvol-minvol)))
			tick.append(((timestamps[x]-mint)/(maxt-mint)))
			normd.append(tick)
		tickerdata = np.array(normd, np.float16)
		normeddata.append(tickerdata)
	normeddata = np.nan_to_num(normeddata)
	print("Done normalizing")

	# Saving #
	data = (np.array(normeddata), outputdata)
	file = open(data_path+f'/getandsorteod/data_to_np/final_data_{starttime[:2]}_{starttime[3:]}_{n_borders}.pkl', 'wb')
	pickle.dump(borders, file)
	pickle.dump(data, file)
	file.close()
	print("done")

# data_to_np()