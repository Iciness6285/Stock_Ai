import pickle
from path import data_path, script_path
trading_days = pickle.load(open('./getandsorteod/get_data/non_trading_days.pkl', 'rb'))


def add_holidays():    
	add = ['2023-01-02','2023-01-16','2023-02-20','2023-04-07',
	'2023-05-29',
	'2023-06-19',
	'2023-07-04',
	'2023-09-04',
	'2023-11-23',
	'2023-11-24',
	'2023-12-25']
	for i in range(len(add)):
		trading_days.append(add[i])
	pickle.dump(trading_days, open('./getandsorteod/get_data/non_tradinghshs_days.pkl', 'wb'))

# add_holidays()

def add_weekends():
	from datetime import timedelta, date
	d0 = date(2022, 12, 26)
	d1 = date(2023,12, 31)
	delta = d1 - d0
	weekends = []
	for i in range(delta.days):
		if d0.weekday() == 5 or d0.weekday() == 6:
			weekends.append(str(d0))
		d0 += timedelta(days=1)
	for i in range(len(weekends)):
		trading_days.append(weekends[i])
	pickle.dump(trading_days, open('C:/Users/flore/OneDrive/programs/stock_ai_scripts/getandsorteod/get_data/non_trading_days.pkl', 'wb'))

# add_weekends()