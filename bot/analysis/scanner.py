import pandas as pd
from bot.config import settings
from bot.utils.logger import logger
from bot.utils.blacklist_manager import BlacklistManager

class MarketScanner:
    def __init__(self, broker):
        self.broker = broker
        self.blacklist = BlacklistManager()

    def scan_and_select(self, top_n=3):
        logger.info("📡 Scanning Market...")
        blocked = self.blacklist.get_blacklist()
        valid_pool =
        
        if not valid_pool:
            logger.warning("All stocks are blacklisted.")
            return

        try:
            quotes = self.broker.kite.quote(valid_pool)
            data_list =

            for symbol, data in quotes.items():
                ohlc = data.get('ohlc', {})
                last = data.get('last_price', 0)
                close = ohlc.get('close', 0)
                if close == 0: continue
                
                change_pct = ((last - close) / close) * 100
                data_list.append({
                    'symbol': symbol,
                    'abs_change': abs(change_pct)
                })

            df = pd.DataFrame(data_list)
            # Pick highest volatility
            df = df.sort_values(by='abs_change', ascending=False)
            
            selected = df.head(top_n)['symbol'].tolist()
            logger.success(f"✅ Scanner Picked: {selected}")
            return selected
        except Exception as e:
            logger.error(f"Scanner Failed: {e}")
            return valid_pool[:top_n]

