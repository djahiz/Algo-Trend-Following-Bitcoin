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
	
	if close >= price_up_open or close <= price_down_open:
		state['CloseConfirmation'] += 1
	else:
		state['CloseConfirmation'] = 0

	if state['WaitCloseLong'] and close <= price_down_close:
		state['WaitCloseLong'] = False

	if state['WaitCloseShort'] and close >= price_up_close:
		state['WaitCloseShort'] = False

	if close >= price_up_open and not(state['Short']) and not(state['Long']) and not state['WaitCloseLong'] and state['CloseConfirmation'] >= CLOSE_CONFIRMATION:
		gain = -FEE
		result = add_order(db, cursor, cur_timestamp, "buy", "Open", "ZEUR", gain, state)
		if not result['error']:
			state = result['state']
	
	if close <= price_down_open and not(state['Long']) and not(state['Short'])  and not state['WaitCloseShort'] and state['CloseConfirmation'] >= CLOSE_CONFIRMATION:
		gain = -FEE
		result = add_order(db, cursor, cur_timestamp, "sell", "Open", "XXBT", gain, state)
		if not result['error']:
			state = result['state']

	if(state['Long'] and close > state['ExtremeValue']):
		state['ExtremeValue'] = close

	if(state['Short'] and close < state['ExtremeValue']):
		state['ExtremeValue'] = close

	if state['Long'] and state['ExtremeValue'] > state['OpenPrice']*(1+BARRIER):
		state['Barrier'] = True

	if state['Short'] and state['ExtremeValue'] < state['OpenPrice']*(1-BARRIER):
		state['Barrier'] = True

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

	if state['Long'] and close < state['ExtremeValue']*(1-(MAX_LOSS*(1-state['Barrier'])+MAX_LOSS_BARRIER*state['Barrier'])):
		gain = close/state['OpenPrice']-1-FEE
		result = add_order(db, cursor, cur_timestamp, "sell", "Close", "XXBT", gain, state)
		if not result['error']:
			state['WaitCloseShort'] = True
			state = result['state']

	if state['Short'] and close > state['ExtremeValue']*(1+(MAX_LOSS*(1-state['Barrier'])+MAX_LOSS_BARRIER*state['Barrier'])):
		gain = 1-close/state['OpenPrice']-FEE
		result = add_order(db, cursor, cur_timestamp, "buy", "Close", "ZEUR", gain, state)
		if not result['error']:
			state['WaitCloseShort'] = True
			state = result['state']
			
	new_state(db, cursor, (cur_timestamp, state['Long'], state['Short'], state['CloseConfirmation'], state['OpenPrice'], state['ClosePrice'], state['ExtremeValue'], state['Barrier'], state['WaitCloseLong'], state['WaitCloseShort']))

	print("Add to bot_state: time: "+ str(datetime.fromtimestamp(cur_timestamp)) +"; pos_long: "+str(state['Long'])+"; pos_short: "+str(state['Short'])+"; open_position: "+str(state['OpenPrice'])+"; close_position: "+str(state['ClosePrice'])+"; extreme: "+str(state['ExtremeValue'])+"; barrier: "+str(state['Barrier'])+"")

	print("Current price " + str(close))
	print("Price open long position: " + str(price_up_open))
	print("Price open short position: " + str(price_down_open))
	print("Price close long position: " + str(price_up_close))
	print("Price close short position: " + str(price_down_close))