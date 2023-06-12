import time
from calendar import timegm
from datetime import datetime, timedelta
import pytz
import pickle

#### required functions #####
def todatetime(t): # Converts unixsec to string, returns exact time "yyyy-m-d H:M:S"
	a = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime((t)))
	return a

def tounix(t):	   # Converts string to unixsec, returns timestamp at 00:00
	a = timegm(time.strptime(t, "%Y-%m-%d"))
	return a

def return_time_deviation(date):	# returns the correct time deviation, based on edt/est
	datetime_time = datetime.strptime(date, '%Y-%m-%d')
	if bool(pytz.timezone('America/New_York').dst(datetime_time, is_dst=None)) == True:
		time_deviation = 4
	else:
		time_deviation = 5
	return time_deviation


def is_data_correctly_labeled(data, time_deviation):
	# checks, if data has timestamps prior to 8:00/9:00 UTC
	# returns bool
	for i in range(len(data)):
		oclock = data[i]["datetime"][11:]
		hours = int(oclock[:2])
		if hours <= 3+time_deviation and hours>=1:
			return False
	return True

def is_data_in_uniform_timezones(data, time_deviation):
	# checks, if data is in the same timezone in the beginning, then in the end
	# returns bool
	if return_time_deviation(todatetime(data[0]["timestamp"])[:10]) != time_deviation:
		return False
	else:
		return True	


def getholidays():
	with open(f"./holidays_2.txt") as f:
		fulllist = f.read().replace('\n', ' ').split()
	months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
	l = []
	for i in range(len(fulllist)):
		if i % 9 == 0:
			t = months[fulllist[i]]
			l.append(t)
		if i % 9 == 1:
			l.append(fulllist[i][:2])
		if i % 9 == 2:
			l.append(fulllist[i])
	hol = []
	for i in range(int(len(l)/3)):
		month = l[i*3]
		day = l[i*3+1]
		year = l[i*3+2]
		d = year+"-"+month+"-"+day
		hol.append(d)
	with open(f"./holidays.txt") as f:
		holiday = f.read().replace('\n', ' ').split()
	for i in range(len(hol)):
		holiday.append(hol[i])
	print(holiday)
	pickle.dump(holiday, open(f'holiday.pkl', 'wb'))

def addweekends():
	from datetime import date
	d0 = date(2004, 1, 1)
	d1 = date(2022,12, 26)
	delta = d1 - d0
	weekends = []
	for i in range(delta.days):
		if d0.weekday() == 5 or d0.weekday() == 6:
			weekends.append(str(d0))
		d0 += timedelta(days=1)
	holiday = pickle.load(open(f'./holiday.pkl', 'rb'))
	for i in range(len(holiday)):
		weekends.append(holiday[i])
	pickle.dump(weekends, open(f'nontradingdays.pkl', 'wb'))

