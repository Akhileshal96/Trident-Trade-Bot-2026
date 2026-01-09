import pandas as pd
from datetime import datetime, timedelta
from bot.utils.logger import logger

class MarketData:
    def __init__(self, broker):
        self.broker = broker

    def get_ohlc(self, symbol, interval):
        try:
            token = self.broker.get_token(symbol)
            if not token: return None
            
            recs = self.broker.kite.historical_data(
                token, 
                datetime.now() - timedelta(days=5), 
                datetime.now(), 
                interval
            )
            df = pd.DataFrame(recs)
            return df
        except Exception as e:
            logger.error(f"Data Error {symbol}: {e}")
            return None

