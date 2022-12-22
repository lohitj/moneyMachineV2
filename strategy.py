def selection_coin(close_final,bbands_final,bbands_previous_candle_long,rsi_final,pair):
	if close_final > bbands_final and rsi_final > 90:
		print("Found one")
		return "Short"
	elif rsi_final < 12 and close_final < bbands_previous_candle_long:
		print("Found One")
		return "Long"
	else:
		print(rsi_final,close_final,bbands_final)
def place_order(close_final,bbands_final,bbands_current_candle_long,selection_coin_flag):
	if close_final < bbands_final and selection_coin_flag == "Short": 
		return "Short"
	elif close_final > bbands_current_candle_long and selection_coin_flag == "Long":
		return "Long"
	else:
		print("Not Selected")
def calculate_time_order_place(df_klines,index):
	avg_time=[]
	Total_sum_ohlc = df_klines.loc[index+1]['Open']+df_klines.loc[index+1]['High']+df_klines.loc[index+1]['Low']+df_klines.loc[index+1]['Close']
	print(Total_sum_ohlc)
	Average_ohlc = Total_sum_ohlc/4
	print(Average_ohlc)
	timestamp_order_place=df_klines.loc[index]['Date']
	avg_time.append(Average_ohlc)
	avg_time.append(timestamp_order_place)
	return avg_time
def calculate_close_order(close_price,selection_coin_flag):
	if selection_coin_flag == "Short":
		close_price=close_price*0.992
		return close_price
	else:
		close_price=close_price*1.008
		return close_price
def calculate_liq_price(close_price):
	close_price=close_price*1.5
	return close_price
