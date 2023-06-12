import pickle
from helperfunctions import tounix, return_time_deviation
from datetime import datetime, timedelta
import json
import time
import urllib.request
from path import data_path, script_path

#### required constants ####
global apitoken
apitoken = "YOUR-API-KEY"	# insert your api key, which you can get from eodhd.
apitoken = "demo"

n_days_insgesamt = 6 				# includes 1 tradingday + 5 previous days
n_days_danach = 5 					# wether to include days after event


def getdata(divided_by=1, number=1):
	nontradingdays = pickle.load(open(script_path+f'/getandsorteod/get_data/non_trading_days.pkl', 'rb'))
	eventlist = pickle.load(open(script_path+f'/getandsorteod/list_of_events/list_of_events.pkl', 'rb'))
	eoddata = []

	beginning_n = int(len(eventlist)/divided_by*(number-1))
	ending_n	= int(len(eventlist)/divided_by*number)
	eventlist = eventlist[beginning_n:ending_n]

	for i in range(int(len(eventlist)/2)):
		starttimer = time.perf_counter()
		ticker    = eventlist[i*2]
		eventdate = eventlist[i*2+1]
		info = [ticker, eventdate]
		endtime = tounix(eventdate) + 20*3600+return_time_deviation(eventdate)*3600-60
		n = 1
		while n != n_days_insgesamt:
			eventdate_dt = datetime.strptime(eventdate, '%Y-%m-%d')
			eventdate_dt += timedelta(days=-1)
			eventdate = datetime.strftime(eventdate_dt, '%Y-%m-%d')
			if eventdate not in nontradingdays:
				n += 1
				info.append(eventdate)
		startdate = eventdate
		starttime = tounix(startdate) + 4*3600+return_time_deviation(startdate)*3600
		
		if n_days_danach != 0:		# if you want days after the event included, set n_days_danach != 0
			eventdate = eventlist[i*2+1]
			n = 0
			while n != n_days_danach:
				eventdate_dt = datetime.strptime(eventdate, '%Y-%m-%d')
				eventdate_dt += timedelta(days=1)
				eventdate = datetime.strftime(eventdate_dt, '%Y-%m-%d')
				if eventdate not in nontradingdays:
					n += 1
					info.append(eventdate)
			endtime = tounix(eventdate) + 20*3600+return_time_deviation(eventdate)*3600-60

		interval, fmt, order = "1m", "json", "a"
		requesturl = f"https://eodhistoricaldata.com/api/intraday/{ticker}.US?api_token={apitoken}&interval={interval}&fmt={fmt}&order={order}&from={starttime}&to={endtime}"
		print(requesturl)
		# print(info)

		# comment out the following if you dont have a valid api key, and if you want to see, if the code above works.
	
		with urllib.request.urlopen(requesturl) as url: 						# getdata
			data_request = json.load(url)
			data_request.append(info)
			eoddata.append(data_request)
		endttimer = time.perf_counter()
		print("Nr. "+str(i)+": "+str(round(i/int(len(eventlist)/2)*100,2))+"%, "+str(round(endttimer-starttimer, 2))+ "s")
	# print(eoddata)
	pickle.dump(eoddata, open(data_path+f'/getandsorteod/get_data/rawdata_{str(number)}-{str(divided_by)}.pkl', 'wb'))

# getdata()