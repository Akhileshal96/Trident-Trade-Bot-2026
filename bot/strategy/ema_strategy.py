import pandas_ta as ta

class Strategy:
    def analyze(self, df):
        # 9/21 EMA Aggressive Crossover
        df['EMA_9'] = ta.ema(df['close'], length=9)
        df['EMA_21'] = ta.ema(df['close'], length=21)
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        signal = "NEUTRAL"
        if prev['EMA_9'] <= prev['EMA_21'] and curr['EMA_9'] > curr['EMA_21']:
            signal = "BUY"
        elif prev['EMA_9'] >= prev['EMA_21'] and curr['EMA_9'] < curr['EMA_21']:
            signal = "SELL"
            
        return signal, curr['close']

