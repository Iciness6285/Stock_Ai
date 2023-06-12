import pickle
from path import data_path
from helperfunctions import tounix, return_time_deviation, todatetime
import numpy as np
import matplotlib.pyplot as plt

n_days_insgesamt = 6
def presort(n_days_after=0):
	presorted_data = []
	for i in range(41):
		print(round((i+1)/0.41,1))
		rawdata = pickle.load(open(data_path+f'/getandsorteod/get_data/rawdata_{i+1}-41.pkl', 'rb'))
		for x in range(len(rawdata)):
			if len(rawdata[x]) >= 3000:
				rawdata_filtered = []
				info = rawdata[x][-1]
				tickername = info[0]
				eventdate = info[1]
				firstdate = info[n_days_insgesamt]
				if n_days_after == 0:
					lastdate = eventdate
				else:	
					lastdate = info[n_days_insgesamt+n_days_after]
				for c in range(len(rawdata[x])-1):
					if rawdata[x][c]["timestamp"] < tounix(lastdate)+25*3600:
						rawdata_filtered.append(rawdata[x][c])
				presorted_data.append(rawdata_filtered)
			# print(len(rawdata_filtered))
		print(len(presorted_data))		
	pickle.dump(presorted_data, open(data_path+f'/getandsorteod/clean_data/presorted_{n_days_after}.pkl', 'wb'))

# presort()



def fillupdata(n_days_after=0):
	data = pickle.load(open(data_path+f'/getandsorteod/clean_data/presorted_{n_days_after}.pkl', 'rb'))
	filledupdata, wrongly_labeled = [], []
	for i in range(len(data)):
		try:
			empty_ticker_list = []
			tradingdays = []
			tickerdata = data[i]
			n, count = 0, 0
			time_deviation = return_time_deviation(todatetime(tickerdata[count]["timestamp"])[:10])
			lastdate = todatetime(tickerdata[-1]["timestamp"]-time_deviation*3600)[:10]
			while n != n_days_insgesamt:								# creates list of trading days
				time_deviation = return_time_deviation(todatetime(tickerdata[count]["timestamp"])[:10])
				currentday = todatetime(tickerdata[count]["timestamp"]-time_deviation*3600)[:10]
				if currentday!=lastdate:
					tradingdays.append(currentday)
					n += 1
					lastdate = currentday
				count += 1
			for x in range(n_days_insgesamt):							# creates empty_list with correct timestamps
				tradingday = tradingdays[x]
				firsttime = tounix(tradingday) + 4*3600+return_time_deviation(tradingday)*3600
				for c in range(960):
					empty_ticker_list.append(firsttime+c*60)

			for x in range(len(tickerdata)):						# replace timestamps with existing data
				timestamp_index = empty_ticker_list.index(tickerdata[x]["timestamp"])
				empty_ticker_list[timestamp_index] = tickerdata[x]

			for x in range(len(empty_ticker_list)):					# fills up missing entries
				if x == 0:
					number = empty_ticker_list.index(tickerdata[0])
					previous_entry = {"open": tickerdata[0]["open"], "high": tickerdata[0]["high"], "low": tickerdata[0]["low"], \
										"close": tickerdata[0]["close"], "volume": 0, "timestamp": tickerdata[0]["timestamp"]-number*60-60}
				else:	
					previous_entry = empty_ticker_list[x-1]
				if isinstance(empty_ticker_list[x], int):
					missing_entry = {"open": previous_entry["open"], "high": previous_entry["high"], "low": previous_entry["low"], \
										"close": previous_entry["close"], "volume": 0, "timestamp": previous_entry["timestamp"]+60}
					empty_ticker_list[x] = missing_entry	
			filledupdata.append(empty_ticker_list)
		except:
			print("error")
			wrongly_labeled.append(i)
		print(round(i/len(data)*100,2))
	inputdatafull = []
	attributes = ["open", "high", "low", "close", "volume", "timestamp"]
	for i in range(len(filledupdata)):										# brings form into np.array(array(array(...)))
		tickerdata = []
		starting_timestamp = filledupdata[i][0]["timestamp"]
		for x in range(len(filledupdata[i])):
			tickvalues = []
			for c in range(5):
				tickvalues.append(filledupdata[i][x][attributes[c]])
			tickvalues.append(int((filledupdata[i][x]["timestamp"]-starting_timestamp)/60))	
			tickerdata.append(np.array(tickvalues, np.float16))
		if (tickerdata[5130][0]/tickerdata[4560][3]-1)*100 > 19:
			inputdatafull.append(np.array(tickerdata))
	print(wrongly_labeled)
	print(len(wrongly_labeled))
	np.save(data_path+f'/getandsorteod/clean_data/cleaned_data_{n_days_after}.npy', inputdatafull)
	pickle.dump(wrongly_labeled, open(data_path+f'/getandsorteod/clean_data/wrongly_labeled.pkl', 'wb'))

# fillupdata()



def plot_cleaned_data(n_days_after=0):
	data = np.load(data_path+f"/getandsorteod/clean_data/cleaned_data_{n_days_after}.npy")
	for x in range(len(data)):
		val_1 = []
		val_2 = []
		val_3 = []
		val_4 = []
		prev_day_close = data[x][4560][3]
		event_day_open = data[x][5130][0]
		gap = (event_day_open/prev_day_close - 1)*100
		for i in range(5760):
			val_1.append(data[x][i][0])
			val_2.append(data[x][i][1])
			val_3.append(data[x][i][2])
			val_4.append(data[x][i][3])
		plt.plot(val_1)
		plt.plot(val_2)
		plt.plot(val_3)
		plt.plot(val_4)
		plt.xlim([0, 6000])
		plt.axhline(y=prev_day_close, xmax=4560/6000, color='black')
		plt.axhline(y=event_day_open, xmax=5130/6000, color='red')
		y_min, y_max = plt.ylim()
		plt.text(1500, y_min+(y_max-y_min)*0.8, f'The Gap is: {round(gap)}%', fontsize=10)
		plt.text(1500, y_min+(y_max-y_min)*0.6, f'Event day open: {round(float(event_day_open), 2)}$', fontsize=10)
		plt.text(1500, y_min+(y_max-y_min)*0.5, f'Previous day close: {round(float(prev_day_close), 2)}$', fontsize=10)
		plt.show()

# plot_cleaned_data()