from path import script_path, data_path
import pickle
import time
import json
import urllib.request

global apitoken
apitoken = "YOUR-API-KEY"	# insert your api key, which you can get from eodhd.
# apitoken = "demo"

def getdailydata(number, divided_by=1):
### gets all the daily data for all of the tickers using eodhd api
### You can download it in batches, using "divided_by" and "number"
	startdate, enddate = "2004-1-1", "2022-11-09"
	period, fmt, order = "d", "json", "a"
	dailydata = []

	with open(script_path+f'/getandsorteod/list_of_events/ListOfTickers.txt') as f:
		fulllist = f.read().replace('\n', ' ').split()
	beginning_n = int(len(fulllist)/divided_by*(number-1))
	ending_n	= int(len(fulllist)/divided_by*number)
	fulllist = fulllist[beginning_n:ending_n]
	errorlist = []
	for i in range(len(fulllist)):
		starttimer = time.perf_counter()
		ticker = fulllist[i]
		try:
			if i%999==0 and i!=0: # because EODHD only allows 1000 requests per minute
				time.sleep(61)
			requesturl = f"https://eodhistoricaldata.com/api/eod/{ticker}.US?api_token={apitoken}&period={period}&fmt={fmt}&order={order}&from={startdate}&to={enddate}"
			with urllib.request.urlopen(requesturl) as url:
				data_request = json.load(url)
				data_request.append(f"{ticker}")
				dailydata.append(data_request)
		except:
			print(ticker)
			errorlist.append(ticker)	
		endttimer = time.perf_counter()
		print("Nr. "+str(i)+": "+str(round(i/int(len(fulllist))*100,2))+"%, "+str(round(endttimer-starttimer, 2))+ "s")

	pickle.dump(dailydata, open(data_path+f'/getandsorteod/list_of_events/dailydata_{number}.pkl', 'wb'))
	pickle.dump(errorlist, open(data_path+f'/getandsorteod/list_of_events/dailydata_errorlist_{number}.pkl', 'wb'))

# getdailydata(1,divided_by=1)


def getevents(): # dailydata -->  eventlist
### gets all the events, which match the criteria (Gap>20%)
	dailydata = pickle.load(open(data_path+f"/getandsorteod/list_of_events/dailydata.pkl", 'rb'))
	print("success")
	eventlist = []
	failed	  = []
	for i in range(len(dailydata)):
		try:
			for x in range(1, int(len(dailydata[i])-1)):
				if (dailydata[i][x]["open"]/dailydata[i][x-1]["close"]) >= 1.2: # Gap>20%
					eventlist.append(dailydata[i][-1])
					eventlist.append(dailydata[i][x]["date"])					
		except:
			failed.append(i)
		print(i/len(dailydata))
	pickle.dump(eventlist, open(script_path+f"/getandsorteod/list_of_events/list_of_events.pkl", 'wb'))
	print(len(eventlist))
	print(eventlist[-10:])
	print(len(failed))

# getevents()