"""
    Database module
    ======================
  
    :Inputs:
   
    
    :Outputs:
 
"""
import krakenex
from settings import *
from mail import *
from data import *
import math

def add_order(db, cursor, cur_timestamp, type_order, way, currency, gain, state):
	try:
		kraken = krakenex.API(key = KEY, secret = SECRET)
	except Exception as e:
		print_logs(LOG_ERROR, "An error occurred when request kraken api " + str(e.args[0]))
		return {'error': True, 'state': state}
	else:
		json = kraken.query_private(method = 'Balance')
		balance = float(json['result'][currency])
		json = kraken.query_public('Ticker', 'pair=XXBTZEUR')
		if type_order == "buy":
			ask = float(json['result']['XXBTZEUR']['a'][0])
			volume = round(balance*0.9/ask,5)
		else:
			volume = balance
		json = kraken.query_private('AddOrder', {'pair':'XXBTZEUR', 'type':type_order, 'ordertype':'market', 'volume':str(volume)})
		if len(json['error']) == 0:
			txid = json['result']['txid'][0]
			json = kraken.query_private('ClosedOrders')
			order = json['result']['closed'][txid]
			new_order(db, cursor, (cur_timestamp, type_order, way, float(order['price']), gain, float(order['cost']), float(order['fee']), float(order['vol'])))
			message = way + " " + type_order + " order at time " + str(datetime.fromtimestamp(cur_timestamp)).replace(":"," ") + " and price " + str(order['price']) + ""
			print(message)
			print_logs(LOG_ORDER, message)
			for email in MAILING_LIST:
				send_mail(MAIL_SERVER, MAIL_PORT, BOT_MAIL, BOT_PASSWD, email, message)
			if way == "Open":
				if type_order == "buy":
					return {'error': False, 'state': {'Long': True, 'Short': False, 'CloseConfirmation': 0, 'OpenPrice': float(order['price']), 'ClosePrice': float(order['price'])*(1-MAX_LOSS), 'ExtremeValue': float(order['price']), 'Barrier': False, 'WaitCloseLong': state['WaitCloseLong'], 'WaitCloseShort': state['WaitCloseShort']}}
				else:
					return {'error': False, 'state': {'Long': False, 'Short': True, 'CloseConfirmation': 0, 'OpenPrice': float(order['price']), 'ClosePrice': float(order['price'])*(1+MAX_LOSS), 'ExtremeValue': float(order['price']), 'Barrier': False, 'WaitCloseLong': state['WaitCloseLong'], 'WaitCloseShort': state['WaitCloseShort']}}
			else:
				return {'error': False, 'state': {'Long': False, 'Short': False, 'CloseConfirmation': 0, 'OpenPrice': 0, 'ClosePrice': 0, 'ExtremeValue': 0, 'Barrier': False, 'WaitCloseLong': state['WaitCloseLong'], 'WaitCloseShort': state['WaitCloseShort']}}
		else:
			print_logs(LOG_ERROR, "An error occurred " + str(json['error']))
			return {'error': True, 'state': state}
