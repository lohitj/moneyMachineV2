def get_macd(df,ta,fast,slow,signal):
	 macd_df=ta.macd(df['Close'],fast=fast, slow=slow, signal=signal, min_periods=None, append=True)
	 macd_df_final = macd_df.iloc[-1]
	 return macd_df_final.iloc[0],macd_df_final.iloc[1],macd_df_final.iloc[2]
def get_rsi_value(df,ta,length,index):
	rsi=ta.rsi(df['Close'],length=length)
	rsi_final = rsi.iloc[index]
	return rsi_final
