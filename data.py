"""
    Database module
    ======================
  
    :Inputs:
   
    
    :Outputs:
 
"""
import sqlite3
import os
from logs import *
from settings import *

def connexion(db_name):
	if not os.path.isfile(db_name):
		raise Exception("Database not found")
	try:
		db = sqlite3.connect(db_name)
	except sqlite.Error as e:
		raise e
	else:
		return db

def get_cursor(db = None):
	return db.cursor()

def get_last_time(cursor):
	try:
		cursor.execute("SELECT LAST_TIMESTAMP FROM data_btc ORDER BY LAST_TIMESTAMP DESC LIMIT 1")
	except Exception as e:
		print_logs(LOG_ERROR, "An error occurred " + e.args[0])
	else:
		return cursor.fetchone()

def get_current_state(cursor):
	try:
		result = cursor.execute("SELECT LONG,SHORT,CLOSE_CONFIRMATION,OPEN_PRICE,CLOSE_PRICE,EXTREME_VALUE,BARRIER,WAIT_CLOSE_LONG,WAIT_CLOSE_SHORT FROM bot_state ORDER BY LAST_TIMESTAMP DESC LIMIT 1")
	except Exception as e:
		return {'Long': False, 'Short': False, 'CloseConfirmation': 0, 'OpenPrice': 0, 'ClosePrice': 0, 'ExtremeValue': 0, 'Barrier': False, 'WaitCloseLong': False, 'WaitCloseShort': False}
	else:
		result = result.fetchone()
		if result == None:
			return {'Long': False, 'Short': False, 'CloseConfirmation': 0, 'OpenPrice': 0, 'ClosePrice': 0, 'ExtremeValue': 0, 'Barrier': False, 'WaitCloseLong': False, 'WaitCloseShort': False}
	return {'Long': result[0], 'Short': result[1], 'CloseConfirmation': result[2], 'OpenPrice': result[3], 'ClosePrice': result[4], 'ExtremeValue': result[5], 'Barrier': result[6], 'WaitCloseLong': result[7], 'WaitCloseShort': result[8]}

def new_order(db, cursor, inputs):
	try:
		cursor.execute("INSERT INTO data_order(LAST_TIMESTAMP,ORDRE,WAY,PRICE,GAIN,COST,FEE,VOLUME) VALUES (?,?,?,?,?,?,?,?)", inputs)
		db.commit()
	except Exception as e:
		print_logs(LOG_ERROR, "An error occurred" + e.args[0])


def new_state(db, cursor, inputs):
	try:
		cursor.execute("INSERT INTO bot_state(LAST_TIMESTAMP,LONG,SHORT,CLOSE_CONFIRMATION,OPEN_PRICE,CLOSE_PRICE,EXTREME_VALUE,BARRIER,WAIT_CLOSE_LONG,WAIT_CLOSE_SHORT) VALUES (?,?,?,?,?,?,?,?,?,?)", inputs)
		db.commit()
	except Exception as e:
		print_logs(LOG_ERROR, "An error occurred" + e.args[0])

def new_data_row(db, cursor, inputs):
	try:
		cursor.execute("INSERT INTO data_btc(LAST_TIMESTAMP,OPEN,HIGH,LOW,CLOSE,MEAN_OPEN,MEAN_CLOSE,VOL_OPEN,VOL_CLOSE,PRICE_UP_OPEN,PRICE_DOWN_OPEN,PRICE_UP_CLOSE,PRICE_DOWN_CLOSE,VOLUME) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",inputs)
		db.commit()
	except Exception as e:
		print_logs(LOG_ERROR, "An error occurred " + e.args[0])
