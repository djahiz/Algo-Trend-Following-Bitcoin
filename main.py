from algo import *
import urllib3

try:
	db = connexion(DB_NAME)
	cursor = get_cursor(db)
except Exception as e:
	print_logs(LOG_ERROR, "An error occurred during DB connection " + e.args[0])
else:
	pass

count = False

while(1):
	
	try:
		last_time = get_last_time(cursor)
	except Exception as e:
		print_logs(LOG_ERROR, "An eror occured while trying to get last time " + e.args[0])
		time.sleep(5)
		pass
	else:
		try:
			kraken = krakenex.API()
			if(last_time == None):
				json = kraken.query_public('OHLC', 'pair=XXBTZEUR')
			else:
				json = kraken.query_public('OHLC', {'pair':'XXBTZEUR','since':''+str(last_time[0])+''})
		except urllib3.exceptions.MaxRetryError:
			time.sleep(5)
			pass
		except Exception as e:
			print_logs(LOG_ERROR, "An error occured while trying to get OHLC data " + e.args[0])
			pass
		else:
			for arr in json['result']['XXBTZEUR']:
				if not count:
					if cursor.execute("SELECT count(CLOSE) FROM data_btc").fetchone()[0] >= max(SIZE_HISTO_OPEN,SIZE_HISTO_CLOSE):
						count = True

				current_time = int(arr[0])
				close = float(arr[4])
				moyenne_open = 0
				moyenne_close = 0
				vol_open = 0
				vol_close = 0
				price_up_open = 0
				price_down_open = 0
				price_up_close = 0
				price_down_close = 0

				if(count):
					get_data = False
					while not get_data:
						try:
							table = pandas.read_sql_query("SELECT CLOSE FROM data_btc ORDER BY LAST_TIMESTAMP DESC LIMIT " + str(max(SIZE_HISTO_OPEN,SIZE_HISTO_CLOSE)) + "", db)
						except Exception as e:
							print_logs(LOG_ERROR, "An error occurred" + e.args[0])
							time.sleep(1)
							pass
						else:
							get_data = True
					moyenne_open = table.loc[:SIZE_HISTO_OPEN,'CLOSE'].mean()
					moyenne_close = table.loc[:SIZE_HISTO_CLOSE,'CLOSE'].mean()
					vol_open = table.loc[:SIZE_HISTO_OPEN,'CLOSE'].std()
					vol_close = table.loc[:SIZE_HISTO_CLOSE,'CLOSE'].std()
					price_up_open = moyenne_open+SIZE_BANDE_OPEN*vol_open
					price_down_open = moyenne_open-SIZE_BANDE_OPEN*vol_open
					price_up_close = moyenne_close+SIZE_BANDE_CLOSE*vol_close
					price_down_close = moyenne_close-SIZE_BANDE_CLOSE*vol_close

				inputs = (current_time, arr[1], arr[2], arr[3], close, moyenne_open, moyenne_close, vol_open, vol_close, price_up_open, price_down_open, price_up_close, price_down_close, arr[6])
				
				new_data_row(db, cursor, inputs)
				
				print("Add to data_btc values for time: " + str(datetime.fromtimestamp(current_time)) + "")

			if(count):
				try:
					algo_trading(db, cursor, current_time, price_up_open, price_down_open, price_up_close, price_down_close, close)
				except Exception as e:
					print_logs(LOG_ERROR, "An error occurred during call of algo_trading " + e.args[0])
					pass
			
			time.sleep(SLEEP_TIME)

input("Press any key...")

db.close()