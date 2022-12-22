from binance.client import Client
import pandas as pd
from binance.um_futures import UMFutures
from data import DataLoader
import pandas_ta as ta
from helpers import momentum
from helpers import standards
from helpers import volatility
from strategy import strategy
api_key = "dx2nfGJrM6j3YuxU6fDNhz60jJHzdh3scK3z0ZlNW8VF0OxNKf9BC9yveWQfRH01"
api_secret = "AkYJ7ZLZd5K8Mkb8zEI5Z5riXVloiKGsoZFuzjgcAVt7Z2VfNhMi9eInMJhhp2qi"
client = Client(api_key, api_secret)
interval = Client.KLINE_INTERVAL_5MINUTE
sma_length = 10
ema_length = 26
def final():
	usdtpairs = DataLoader.get_all_usdt_pairs(client)
	sma_list=[]
	ema_list=[]
	rsi_list=[]
	bbands_list=[]
	close_price=[]
	selected_list=[]
	for pair in usdtpairs:
		message = DataLoader.get_klines(pair,client,interval)
		df_klines = DataLoader.prepare_dataframe(message,pd)
		sma_final = standards.get_sma(df_klines,ta,sma_length)
		ema_final = standards.get_ema(df_klines,ta,ema_length)
		close_final = df_klines.iloc[-1]['Close']
		rsi_final=momentum.get_rsi_value(df_klines,ta,6,-1)
		bbands_final=volatility.get_bollinger_bands(df_klines,ta,20,-1)['BBU_20_2.0'].iloc[-1].item()
		selcted_coin=strategy.selection_coin(close_final,bbands_final,rsi_final,pair)
		selected_list.append(selection_coin)
		sma_list.append(sma_final)
		ema_list.append(ema_final)
		rsi_list.append(rsi_final)
		close_price.append(close_final)
		bbands_list.append(bbands_final)
	df_final= pd.DataFrame({"Pairs":usdtpairs,"SMA_10":sma_final,"Close Price":close_price,"EMA_26":ema_final,"RSI_6":rsi_list,"BBU_20_2":bbands_list})
	return df_final,selected_list
def macd_variables():
	message = DataLoader.get_klines('BTCUSDT',client,interval)
	df_klines = DataLoader.prepare_dataframe(message,pd)
	macd_dif,macd,macd_dea = momentum.get_macd(df_klines,ta,12,26,9)
	return macd_dif,macd,macd_dea
def rsi_value():
	message = DataLoader.get_klines('BTCUSDT',client,interval)
	df_klines = DataLoader.prepare_dataframe(message,pd)
	print(df_klines)
	print(momentum.get_rsi_value(df_klines,ta,6))
	print(volatility.get_bollinger_bands(df_klines,ta,20)['BBU_20_2.0'].iloc[-1].item())
def order_selection(selected_list):
	for pair in selected_list:
		message = DataLoader.get_klines(pair,client,interval)
		df_klines = DataLoader.prepare_dataframe(message,pd)
		close_final = df_klines.iloc[-1]['Close']
		bbands_final=volatility.get_bollinger_bands(df_klines,ta,20)['BBU_20_2.0'].iloc[-1].item()
		order_flag=strategy.place_order(close_final,bbands_final)
		print(order_flag)	
if __name__ == '__main__':
	df_final,selected_list=final()
	if len(selected_list)!= 0:
		order_selection(selected_list)

