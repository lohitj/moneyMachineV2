def get_sma(df,ta,length):
	sma=ta.sma(df["Close"], length=length)
	sma_final = sma.iloc[-1]
	return sma_final
def get_ema(df,ta,length):
	ema=ta.ema(ta.ohlc4(df["Open"], df["High"], df["Low"], df["Close"]), length=length)
	ema_final = ema.iloc[-1]
	return ema_final