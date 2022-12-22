
def get_all_usdt_pairs(client):
	info = client.futures_exchange_info()
	usdtpairs = []
	for i in info['symbols']:
	  if 'USDT' in i['symbol'] and 'PERPETUAL' in i['contractType']:
	    usdtpairs.append(i['symbol'])
	return usdtpairs
def get_klines(ticker,client,interval):
	message=client.get_historical_klines(symbol=ticker, interval=interval)
	return message
def prepare_dataframe(message,pd):
	df_klines = pd.DataFrame(message, columns =['Date', 'Open','High','Low','Close','Volume','Close time','Quote asset volume','Number of trades','Taker buy base asset volume','Taker buy quote asset volume','Ignore'])
	df_klines["Open"] = pd.to_numeric(df_klines["Open"], downcast="float")
	df_klines["High"] = pd.to_numeric(df_klines["High"], downcast="float")
	df_klines["Low"] = pd.to_numeric(df_klines["Low"], downcast="float")
	df_klines["Close"] = pd.to_numeric(df_klines["Close"], downcast="float")
	df_klines.drop(index=df_klines.index[-1],axis=0,inplace=True)
	return df_klines
def prepare_custom_data_frame(df_klines,pd):
	df_strategy = pd.DataFrame().assign(Date=df_klines['Date'],Open=df_klines['Open'],High=df_klines['High'],Low=df_klines['Low'],Close=df_klines['Close'],Volume=df_klines['Volume'])
	return df_strategy
def get_historical_data_start_end_date(ticker,client,interval,start_str,end_str):
	message=client.get_historical_klines(symbol=ticker,interval=interval,start_str=start_str, end_str=end_str)
	return message
