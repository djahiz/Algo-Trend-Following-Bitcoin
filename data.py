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
import time

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

def get_histo_order(cursor):
	try:
		cursor.execute("SELECT * FROM data_order ORDER BY LAST_TIMESTAMP DESC LIMIT 10")
	except Exception as e:
		print_logs(LOG_ERROR, "An error occurred " + e.args[0])
	else:
		return cursor.fetchone()

def get_current_state(cursor):
	try:
		result = cursor.execute("SELECT LONG,SHORT,CLOSE_CONFIRMATION_LONG,CLOSE_CONFIRMATION_SHORT,OPEN_PRICE,CLOSE_PRICE,VOLUME_FIAT,VOLUME_CRYPTO,EXTREME_VALUE,BARRIER_LONG,BARRIER_SHORT,WAIT_CLOSE_LONG,WAIT_CLOSE_SHORT FROM bot_state ORDER BY LAST_TIMESTAMP DESC LIMIT 1")
	except Exception as e:
		return {'Long': False, 'Short': False, 'CloseConfirmationLong': 0, 'CloseConfirmationShort': 0, 'OpenPrice': 0, 'ClosePrice': 0, 'VolumeFiat': 0, 'VolumeCrypto': 0, 'ExtremeValue': 0, 'BarrierLong': False, 'BarrierShort': False, 'WaitCloseLong': False, 'WaitCloseShort': False}
	else:
		result = result.fetchone()
		if result == None:
			return {'Long': False, 'Short': False, 'CloseConfirmationLong': 0, 'CloseConfirmationShort': 0, 'OpenPrice': 0, 'ClosePrice': 0, 'VolumeFiat': 0, 'VolumeCrypto': 0, 'ExtremeValue': 0, 'BarrierLong': False, 'BarrierShort': False, 'WaitCloseLong': False, 'WaitCloseShort': False}
	return {'Long': result[0], 'Short': result[1], 'CloseConfirmationLong': result[2], 'CloseConfirmationShort': result[3], 'OpenPrice': result[4], 'ClosePrice': result[5], 'VolumeFiat': result[6], 'VolumeCrypto': result[7], 'ExtremeValue': result[8], 'BarrierLong': result[9], 'BarrierShort': result[10], 'WaitCloseLong': result[11], 'WaitCloseShort': result[12]}

def new_order(db, cursor, inputs):
	save_data = False
	while not save_data:
		try:
			cursor.execute("INSERT INTO data_order(LAST_TIMESTAMP,ORDRE,WAY,PRICE,GAIN,COST,FEE,VOLUME) VALUES (?,?,?,?,?,?,?,?)", inputs)
			db.commit()
		except Exception as e:
			print_logs(LOG_ERROR, "An error occurred while saving new order " + e.args[0])
			time.sleep(3)
			pass
		else:
			save_data = True


def new_state(db, cursor, inputs):
	save_data = False
	while not save_data:
		try:
			cursor.execute("INSERT INTO bot_state(LAST_TIMESTAMP,LONG,SHORT,CLOSE_CONFIRMATION_LONG,CLOSE_CONFIRMATION_SHORT,OPEN_PRICE,CLOSE_PRICE,VOLUME_FIAT,VOLUME_CRYPTO,EXTREME_VALUE,BARRIER_LONG,BARRIER_SHORT,WAIT_CLOSE_LONG,WAIT_CLOSE_SHORT) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", inputs)
			db.commit()
		except Exception as e:
			print_logs(LOG_ERROR, "An error occurred while saving state " + e.args[0])
			time.sleep(3)
			pass
		else:
			save_data = True

def new_data_row(db, cursor, inputs):
	save_data = False
	while not save_data:
		try:
			cursor.execute("INSERT INTO data_btc(LAST_TIMESTAMP,OPEN,HIGH,LOW,CLOSE,MEAN_OPEN,MEAN_CLOSE,VOL_OPEN,VOL_CLOSE,PRICE_UP_OPEN,PRICE_DOWN_OPEN,PRICE_UP_CLOSE,PRICE_DOWN_CLOSE,VOLUME) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",inputs)
			db.commit()
		except Exception as e:
			print_logs(LOG_ERROR, "An error occurred while saving data " + e.args[0])
			time.sleep(3)
			pass
		else:
			save_data = True
