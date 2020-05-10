"""
    Algorithm module
    ======================
  
    :Inputs:
   
    
    :Outputs:
 
"""
from datetime import datetime
from order import *

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

	if state['Long'] and close < state['ExtremeValue']*(1-(MAX_LOSS*(1-state['BarrierLong'])+MAX_LOSS_BARRIER*state['BarrierLong'])):
		gain = close/state['OpenPrice']-1-FEE
		result = add_order(db, cursor, cur_timestamp, "sell", "Close", "XXBT", gain, state)
		if not result['error']:
			state['WaitCloseShort'] = True
			state = result['state']

	if state['Short'] and close > state['ExtremeValue']*(1+(MAX_LOSS*(1-state['BarrierShort'])+MAX_LOSS_BARRIER*state['BarrierShort'])):
		gain = 1-close/state['OpenPrice']-FEE
		result = add_order(db, cursor, cur_timestamp, "buy", "Close", "ZEUR", gain, state)
		if not result['error']:
			state['WaitCloseShort'] = True
			state = result['state']
			
	if state['Long']:
		new_state(db, cursor, (cur_timestamp, state['Long'], state['Short'], state['CloseConfirmationLong'], state['CloseConfirmationShort'], state['OpenPrice'], state['ExtremeValue']*(1-MAX_LOSS), state['VolumeFiat'], state['VolumeCrypto'], state['ExtremeValue'], state['BarrierLong'], state['BarrierShort'], state['WaitCloseLong'], state['WaitCloseShort']))
	elif state['Short']:
		new_state(db, cursor, (cur_timestamp, state['Long'], state['Short'], state['CloseConfirmationLong'], state['CloseConfirmationShort'], state['OpenPrice'], state['ExtremeValue']*(1+MAX_LOSS), state['VolumeFiat'], state['VolumeCrypto'], state['ExtremeValue'], state['BarrierLong'], state['BarrierShort'], state['WaitCloseLong'], state['WaitCloseShort']))
	else:
		new_state(db, cursor, (cur_timestamp, state['Long'], state['Short'], state['CloseConfirmationLong'], state['CloseConfirmationShort'], state['OpenPrice'], state['ClosePrice'], state['VolumeFiat'], state['VolumeCrypto'], state['ExtremeValue'], state['BarrierLong'], state['BarrierShort'], state['WaitCloseLong'], state['WaitCloseShort']))

	print("Add to bot_state: time: "+ str(datetime.fromtimestamp(cur_timestamp)) +"; pos_long: "+str(state['Long'])+"; pos_short: "+str(state['Short'])+"; open_position: "+str(state['OpenPrice'])+"; close_position: "+str(state['ClosePrice'])+"; extreme: "+str(state['ExtremeValue'])+"; BarrierLong: "+str(state['BarrierLong'])+"; BarrierShort: "+str(state['BarrierShort'])+" volume Fiat "+str(state['VolumeFiat']) + " volume Crypto "+str(state['VolumeCrypto']))

	print("Current price " + str(close))
	print("Price open long position: " + str(price_up_open))
	print("Price open short position: " + str(price_down_open))
	print("Price close long position: " + str(price_down_close))
	print("Price close short position: " + str(price_up_close))