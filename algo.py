"""
    Algorithm module
    ======================
  
    :Inputs:
   
    
    :Outputs:
 
"""
from datetime import datetime
from order import *
import pandas

def algo_trading(db,cursor,cur_timestamp,price_up_open,price_down_open,price_up_close,price_down_close,close): 
	
	state = get_current_state(cursor)
	
	if close >= price_up_open:
		state['CloseConfirmationLong'] += 1
	elif close <= price_down_open:
		state['CloseConfirmationShort'] += 1
	else:
		state['CloseConfirmationLong'] = 0
		state['CloseConfirmationShort'] = 0

	if state['WaitCloseLong'] and close <= price_down_close:
		state['WaitCloseLong'] = False

	if state['WaitCloseShort'] and close >= price_up_close:
		state['WaitCloseShort'] = False
	
	if close >= price_up_open and not(state['Short']) and not(state['Long']) and not state['WaitCloseLong'] and state['CloseConfirmationLong'] >= CLOSE_CONFIRMATION_LONG:
		gain = -FEE
		result = add_order(db, cursor, cur_timestamp, "buy", "Open", "ZEUR", gain, state)
		if not result['error']:
			state = result['state']
	
	if close <= price_down_open and not(state['Long']) and not(state['Short'])  and not state['WaitCloseShort'] and state['CloseConfirmationShort'] >= CLOSE_CONFIRMATION_SHORT:
		gain = -FEE
		result = add_order(db, cursor, cur_timestamp, "sell", "Open", "XXBT", gain, state)
		if not result['error']:
			state = result['state']
	
	if(state['Long'] and close > state['ExtremeValue']):
		state['ExtremeValue'] = close

	if(state['Short'] and close < state['ExtremeValue']):
		state['ExtremeValue'] = close

	if state['Long'] and state['ExtremeValue'] > state['OpenPrice']*(1+BARRIER_LONG):
		state['BarrierLong'] = True

	if state['Short'] and state['ExtremeValue'] < state['OpenPrice']*(1-BARRIER_SHORT):
		state['BarrierShort'] = True
		
	if close <= price_down_close and state['Long']:
		gain = close/state['OpenPrice']-1-FEE
		result = add_order(db, cursor, cur_timestamp, "sell", "Close", "XXBT", gain, state)
		if not result['error']:
			state = result['state']

	if close >= price_up_close and state['Short']:
		gain = 1-close/state['OpenPrice']-FEE
		result = add_order(db, cursor, cur_timestamp, "buy", "Close", "ZEUR", gain, state)
		if not result['error']:
			state = result['state']

	if state['Long'] and close < state['ExtremeValue']*(1-(MAX_LOSS_LONG*(1-state['BarrierLong'])+MAX_LOSS_BARRIER*state['BarrierLong'])):
		gain = close/state['OpenPrice']-1-FEE
		result = add_order(db, cursor, cur_timestamp, "sell", "Close", "XXBT", gain, state)
		if not result['error']:
			state = result['state']
			state['WaitCloseLong'] = True

	if state['Short'] and close > state['ExtremeValue']*(1+(MAX_LOSS_SHORT*(1-state['BarrierShort'])+MAX_LOSS_BARRIER*state['BarrierShort'])):
		gain = 1-close/state['OpenPrice']-FEE
		result = add_order(db, cursor, cur_timestamp, "buy", "Close", "ZEUR", gain, state)
		if not result['error']:
			state = result['state']
			state['WaitCloseShort'] = True
	
	if state['Long']:
		new_state(db, cursor, (cur_timestamp, state['Long'], state['Short'], state['CloseConfirmationLong'], state['CloseConfirmationShort'], state['OpenPrice'], state['ExtremeValue']*(1-MAX_LOSS_LONG), state['VolumeFiat'], state['VolumeCrypto'], state['ExtremeValue'], state['BarrierLong'], state['BarrierShort'], state['WaitCloseLong'], state['WaitCloseShort']))
	elif state['Short']:
		new_state(db, cursor, (cur_timestamp, state['Long'], state['Short'], state['CloseConfirmationLong'], state['CloseConfirmationShort'], state['OpenPrice'], state['ExtremeValue']*(1+MAX_LOSS_SHORT), state['VolumeFiat'], state['VolumeCrypto'], state['ExtremeValue'], state['BarrierLong'], state['BarrierShort'], state['WaitCloseLong'], state['WaitCloseShort']))
	else:
		new_state(db, cursor, (cur_timestamp, state['Long'], state['Short'], state['CloseConfirmationLong'], state['CloseConfirmationShort'], state['OpenPrice'], state['ClosePrice'], state['VolumeFiat'], state['VolumeCrypto'], state['ExtremeValue'], state['BarrierLong'], state['BarrierShort'], state['WaitCloseLong'], state['WaitCloseShort']))

	print("Add to bot_state: time: "+ str(datetime.fromtimestamp(cur_timestamp)) +"; pos_long: "+str(state['Long'])+"; pos_short: "+str(state['Short'])+"; open_position: "+str(state['OpenPrice'])+"; close_position: "+str(state['ClosePrice'])+"; extreme: "+str(state['ExtremeValue'])+"; BarrierLong: "+str(state['BarrierLong'])+"; BarrierShort: "+str(state['BarrierShort'])+" volume Fiat "+str(state['VolumeFiat']) + " volume Crypto "+str(state['VolumeCrypto'])+ " WaitCloseLong "+str(state['WaitCloseLong'])+" WaitCloseShort "+str(state['WaitCloseShort']))

	print("Current price " + str(close))
	print("Price open long position: " + str(price_up_open))
	print("Price open short position: " + str(price_down_open))
	print("Price close long position: " + str(price_down_close))
	print("Price close short position: " + str(price_up_close))

	x = datetime.fromtimestamp(cur_timestamp)
	if x.hour % 3 == 0 and x.minute == 0:
		time_mail = x.strftime("%x") + " " + x.strftime("%X").split(":")[0] + "h" + x.strftime("%X").split(":")[1]
		message = "Recapitulatif " + str(time_mail) + "\n"
		message += "Cours actuel " + str(close) + "\n\n"
		if state['Long']:
			message += "Position long ouverte au prix de " + str(state['OpenPrice']) + " euros pour un volume de " + str(state['VolumeCrypto']) + " btc \n"
			message += "Fermeture prevue au prix de " + str(state['ClosePrice']) + "\n\n"
		elif state['Short']:
			message += "Position short ouverte au prix de " + str(state['OpenPrice']) + " euros pour un volume de " + str(state['VolumeFiat']) + " euros \n"
			message += "Fermeture prevue au prix de " + str(state['ClosePrice']) + "\n\n"
		else:
			message += "Aucune position ouverte \n"
			message += "Prochain ordre \n"
			message += "Prix d'ouverture long " + str(price_up_open) + "\n"
			message += "Prix d'ouverture short " + str(price_down_open) + "\n"
			message += "Prix de fermeture long " + str(price_down_close) + "\n"
			message += "Prix de fermeture short " + str(price_up_close) + "\n\n"
		message += "Historique\n"
		histo = pandas.read_sql_query("SELECT * FROM data_order ORDER BY LAST_TIMESTAMP DESC LIMIT 10", db)
		for index, row in histo.iterrows():
			x = datetime.fromtimestamp(row['LAST_TIMESTAMP'])
			time_order = x.strftime("%x") + " " + x.strftime("%X").split(":")[0] + "h" + x.strftime("%X").split(":")[1]
			if row['ORDRE'] == "buy":
				message += str(time_order) + " Achat de " + str(row['VOLUME']) + " btc au prix de " + str(row['PRICE']) + " euros\nGain " + str(round(float(row['GAIN'])*100,2)) + "% \n"
			else:
				message += str(time_order) + " Vente de " + str(row['VOLUME']) + " btc au prix de " + str(row['PRICE']) + " euros\nGain " + str(round(float(row['GAIN'])*100,2)) + "% \n"
		for email in MAILING_LIST:
			send_mail(MAIL_SERVER, MAIL_PORT, BOT_MAIL, BOT_PASSWD, email, message)
