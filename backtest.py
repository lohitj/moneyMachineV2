from binance.client import Client
import pandas as pd
from binance.um_futures import UMFutures
from data import DataLoader
import pandas_ta as ta
from helpers import momentum
from helpers import standards
from helpers import volatility
from strategy import strategy
from datetime import datetime
from simple_salesforce import Salesforce
import datetime
api_key = "dx2nfGJrM6j3YuxU6fDNhz60jJHzdh3scK3z0ZlNW8VF0OxNKf9BC9yveWQfRH01"
api_secret = "AkYJ7ZLZd5K8Mkb8zEI5Z5riXVloiKGsoZFuzjgcAVt7Z2VfNhMi9eInMJhhp2qi"
client = Client(api_key, api_secret)
interval = Client.KLINE_INTERVAL_5MINUTE
start_str="01 Jan, 2021"
year=2021
month=5
day=31
format_datetime = datetime.datetime(year, month, day)
end_str=format_datetime.strftime("%d %b, %Y")
df_placed_orders = pd.DataFrame(columns = ['Open_Date', 'Open_Close_Price','Pair'])
def get_backtest_data(ticker_name):
	message=DataLoader.get_historical_data_start_end_date(ticker_name,client,interval,start_str,end_str)
	df_klines=DataLoader.prepare_dataframe(message,pd)
	return df_klines
def backtest_essentials(df_klines,pair):
	rsi_previous_candle=momentum.get_rsi_value(df_klines,ta,6,-2)
	bbands_previous_candle=volatility.get_bollinger_bands(df_klines,ta,20)['BBU_20_2.0'].iloc[-2].item()
	bbands_current_candle=volatility.get_bollinger_bands(df_klines,ta,20)['BBU_20_2.0'].iloc[-1].item()
	bbands_previous_candle_long=volatility.get_bollinger_bands(df_klines,ta,20)['BBL_20_2.0'].iloc[-2].item()
	bbands_current_candle_long=volatility.get_bollinger_bands(df_klines,ta,20)['BBL_20_2.0'].iloc[-1].item()
	close_previous_candle=df_klines.iloc[-2]['Close']
	close_current_candle=df_klines.iloc[-1]['Close']
	selection_coin_flag=strategy.selection_coin(close_previous_candle,bbands_previous_candle,bbands_previous_candle_long,rsi_previous_candle,pair)
	place_order_flag=strategy.place_order(close_current_candle,bbands_current_candle,bbands_current_candle_long,selection_coin_flag)
	return selection_coin_flag,place_order_flag,pair,rsi_previous_candle,bbands_previous_candle,bbands_current_candle
def order_placed(df_placed_orders,df_klines,selection_coin_flag,place_order_flag,pair):
	if selection_coin_flag is "Short" or selection_coin_flag is "Long" and place_order_flag is "Short" or place_order_flag is "Long":
		timestamp_opened_order=df_klines.iloc[-1]['Date']
		close_price_order=df_klines.iloc[-1]['Close']
		return timestamp_opened_order,close_price_order
	return "False","False"
def order_closed(time_stamp,high_price,low_price,df_placed_orders):
	for index in range(0,len(df_placed_orders)):
		tp_close_price=df_placed_orders.iloc[index]['TP_Close']
		tp_liq_price=df_placed_orders.iloc[index]['TP_Close']*1.5
		if tp_close_price < high_price and tp_close_price > low_price and df_placed_orders.iloc[index]['Status']=='Open':
			print("Order Closed")
			order_id=df_placed_orders.loc[index]['Order_ID']
			sf = Salesforce(username='moneymachine@v1.com', password='Newdelhi2*', security_token='Ja4vbYV930m5dmO3HYdeqh0dJ')
			sf.trade_history__c.create({'Order_history__c':order_id,'Average_Price__c':tp_close_price,'timestamp__c':int(time_stamp),'status__c':'Close'})
			return "Close",index
		elif tp_liq_price < high_price and tp_liq_price > low_price and df_placed_orders.iloc[index]['Status']=='Open':
			print("Order Closed")
			order_id=df_placed_orders.loc[index]['Order_ID']
			sf = Salesforce(username='moneymachine@v1.com', password='Newdelhi2*', security_token='Ja4vbYV930m5dmO3HYdeqh0dJ')
			sf.trade_history__c.create({'Order_history__c':order_id,'Average_Price__c':tp_close_price,'timestamp__c':int(time_stamp),'status__c':'Liq'})
			return "Liq",index
	return "False","False"
def main():
	usdtpairs = DataLoader.get_all_usdt_pairs(client)
	for pair in usdtpairs:
		df_klines=get_backtest_data(pair)
		df_backtest_data=DataLoader.prepare_custom_data_frame(df_klines[:25],pd)
		for index in range(25,len(df_klines)):
			print(pair,index)
			df_backtest_data=df_backtest_data.append({'Date':df_klines.loc[index]['Date'],'Open':df_klines.loc[index]['Open'],'High':df_klines.loc[index]['High'],'Low':df_klines.loc[index]['Low'],'Close':df_klines.loc[index]['Close'],'Volume':df_klines.loc[index]['Volume']},ignore_index = True)
			selection_coin_flag,place_order_flag,pair=backtest_essentials(df_backtest_data,pair)
			timestamp_opened_order,close_price_order=order_placed(df_placed_orders,df_backtest_data,selection_coin_flag,place_order_flag,pair)
			order_closed=(df_klines.loc[index]['High'],df_klines.loc[index]['Low'],df_placed_orders)
			if timestamp_opened_order is not "False":
				df_placed_orders=df_placed_orders.append({'Open_Date':timestamp_opened_order,'Open_Close_Price':close_price_order,'Pair':pair},ignore_index = True)
		print(df_placed_orders)

	print(df_placed_orders)
def salesforce(Avg_Price__c,Created_time__c,symbol__c,rsi__c,current_bollinger__c,previous_bollinger__c,order_id__c,selection_coin_flag,max_n,low,pair):
	sf = Salesforce(username='moneymachine@v1.com', password='Newdelhi2*', security_token='Ja4vbYV930m5dmO3HYdeqh0dJ')
	response=sf.Order_history__c.create({'Average_Price__c':Avg_Price__c,'timestamp__c':int(Created_time__c),'symbol__c':pair,'rsi__c':rsi__c,'current_bollinger__c':current_bollinger__c,'previous_bollinger__c':previous_bollinger__c,'status__c':'Filled','order_id__c':order_id__c,'side__c':selection_coin_flag,'x24h_high__c':max_n,'x24h_low__c':low,'period__c':'Jan_to_may_2021'})
	order_id=response.get('id')
	return order_id
def update_max(high_price,low_price,max_n,low):
	high_price=float(high_price)
	low_price=float(low_price)
	if high_price>max_n:
		max_n=high_price
	elif low>low_price:
		low=low_price
	return max_n,low
def reset_max(index,max_n,low):
	if index%288 == 0:
		max_n=0
		low=100000
	return max_n,low
if __name__ == '__main__':
	pair_list=["FOOTBALLUSDT", "ZILUSDT", "ZENUSDT", "ZECUSDT", "YFIUSDT", "XTZUSDT", "XRPUSDT", "XMRUSDT", "XLMUSDT", "XEMUSDT", "WOOUSDT", "WAVESUSDT", "VETUSDT", "UNIUSDT", "UNFIUSDT", "TRXUSDT", "TOMOUSDT", "THETAUSDT", "SXPUSDT", "SUSHIUSDT", "STORJUSDT", "STMXUSDT", "STGUSDT", "SPELLUSDT", "SOLUSDT", "SNXUSDT", "SKLUSDT", "SFPUSDT", "SANDUSDT", "RVNUSDT", "RUNEUSDT", "RSRUSDT", "ROSEUSDT", "RLCUSDT", "RENUSDT", "REEFUSDT", "QTUMUSDT", "QNTUSDT", "PEOPLEUSDT", "OPUSDT", "ONTUSDT", "ONEUSDT", "OMGUSDT", "OGNUSDT", "OCEANUSDT", "NKNUSDT", "NEOUSDT", "NEARUSDT", "MTLUSDT", "MKRUSDT", "MATICUSDT", "MASKUSDT", "MANAUSDT", "LUNA2USDT", "LTCUSDT", "LRCUSDT", "LPTUSDT", "LITUSDT", "LINKUSDT", "LINAUSDT", "LDOUSDT", "KSMUSDT", "KNCUSDT", "KLAYUSDT", "KAVAUSDT", "JASMYUSDT", "IOTXUSDT", "IOTAUSDT", "IOSTUSDT", "INJUSDT", "IMXUSDT", "ICXUSDT", "ICPUSDT", "HOTUSDT", "HNTUSDT", "HBARUSDT", "GTCUSDT", "GRTUSDT", "GMTUSDT", "GALUSDT", "GALAUSDT", "FTMUSDT", "FOOTBALLUSDT", "FLOWUSDT", "FLMUSDT", "FILUSDT", "ETCUSDT", "EOSUSDT", "ENSUSDT", "ENJUSDT", "EGLDUSDT", "DYDXUSDT", "DUSKUSDT", "DOTUSDT", "DOGEUSDT", "DENTUSDT", "DASHUSDT", "DARUSDT", "CVXUSDT", "CTSIUSDT", "CTKUSDT", "CRVUSDT", "COTIUSDT", "COMPUSDT", "CHZUSDT", "CHRUSDT", "CELRUSDT", "CELOUSDT", "C98USDT", "BNXUSDT", "BLZUSDT", "BLUEBIRDUSDT", "BELUSDT", "BCHUSDT", "BATUSDT", "BANDUSDT", "BALUSDT", "BAKEUSDT", "AXSUSDT", "AVAXUSDT", "AUDIOUSDT", "ATOMUSDT", "ATAUSDT", "ARUSDT", "ARPAUSDT", "APTUSDT", "API3USDT", "APEUSDT", "ANTUSDT", "ANKRUSDT", "ALPHAUSDT", "ALICEUSDT", "ALGOUSDT", "ADAUSDT", "AAVEUSDT", "1INCHUSDT", "1000XECUSDT"]
	for pair in pair_list:
		try:
			df_klines=get_backtest_data(pair)
			df_backtest_data=DataLoader.prepare_custom_data_frame(df_klines[:25],pd)
			max_n=0
			low=100000
			for index in range(25,len(df_klines)):
				print(pair,index)
				df_backtest_data=df_backtest_data.append({'Date':df_klines.loc[index]['Date'],'Open':df_klines.loc[index]['Open'],'High':df_klines.loc[index]['High'],'Low':df_klines.loc[index]['Low'],'Close':df_klines.loc[index]['Close'],'Volume':df_klines.loc[index]['Volume']},ignore_index = True)
				selection_coin_flag,place_order_flag,pair,rsi_previous_candle,bbands_previous_candle,bbands_current_candle=backtest_essentials(df_backtest_data,pair)
				timestamp_opened_order,close_price_order=order_placed(df_placed_orders,df_backtest_data,selection_coin_flag,place_order_flag,pair)
				max_n,low=update_max(df_klines.loc[index]['High'],df_klines.loc[index]['Low'],max_n,low)
				if len(df_placed_orders)!=0:
					closed_flag,place=order_closed(df_klines.loc[index]['Date'],df_klines.loc[index]['High'],df_klines.loc[index]['Low'],df_placed_orders)
					if closed_flag == "Close":
						print(place)
						df_placed_orders.loc[place,['Status']]=['Close']
						df_placed_orders.loc[place,['Close_Time_Stamp']]=[df_klines.loc[index]['Date']]
					elif closed_flag == "Liq":
						print(place)
						df_placed_orders.loc[place,['Status']]=['Liq']
						df_placed_orders.loc[place,['Close_Time_Stamp']]=[df_klines.loc[index]['Date']]
				if timestamp_opened_order != "False":
					avg_time=strategy.calculate_time_order_place(df_klines,index)
					order_id=salesforce(avg_time[0],avg_time[1],pair,rsi_previous_candle,bbands_previous_candle,bbands_current_candle,index,selection_coin_flag,max_n,low,pair)
					tp_close_price=strategy.calculate_close_order(avg_time[0],selection_coin_flag)
					tp_liq_price=strategy.calculate_liq_price(avg_time[0])
					df_placed_orders=df_placed_orders.append({'Order_ID':order_id,'Open_Date':avg_time[1],'Open_Close_Price':avg_time[0],'RSI':rsi_previous_candle,'Previous Upper Band':bbands_previous_candle,'Current Upper Band':bbands_current_candle,'TP_Close':tp_close_price,'Pair':pair,'Status':'Open','Close_Time_Stamp':'','Liq_Price':tp_liq_price,'Order_Side':selection_coin_flag,'24_hour_High':max_n,'24_hour_low':low},ignore_index = True)
				reset_max(index,max_n,low)
				print(df_placed_orders)
			print(df_placed_orders)
		except:
			print("Could Not Exist")

		

