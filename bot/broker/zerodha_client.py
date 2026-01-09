from kiteconnect import KiteConnect
from bot.config import settings
from bot.utils.logger import logger

class ZerodhaClient:
    def __init__(self, kite_instance=None):
        if kite_instance:
            self.kite = kite_instance
        else:
            self.kite = KiteConnect(api_key=settings.KITE_API_KEY)
            self.kite.set_access_token(settings.KITE_ACCESS_TOKEN)

    def get_available_margin(self):
        try:
            margins = self.kite.margins(segment="equity")
            return float(margins.get("net", 0.0))
        except Exception as e:
            logger.error(f"Margin fetch failed: {e}")
            return None

    def load_instruments(self):
        logger.info("Connecting to Zerodha...")
        self.kite.profile() # Test call
        logger.success("✅ Connection Successful.")

    def get_ltp(self, symbol):
        try:
            resp = self.kite.ltp(symbol)
            if resp and symbol in resp:
                return resp[symbol]['last_price']
        except Exception as e:
            logger.error(f"LTP Error: {e}")
        return 0.0

    def place_market_order(self, symbol, side, qty):
        try:
            tx = self.kite.TRANSACTION_TYPE_BUY if side == "BUY" else self.kite.TRANSACTION_TYPE_SELL
            return self.kite.place_order(
                tradingsymbol=symbol.replace("NSE:", ""),
                exchange=self.kite.EXCHANGE_NSE,
                transaction_type=tx,
                quantity=qty,
                variety=self.kite.VARIETY_REGULAR,
                order_type=self.kite.ORDER_TYPE_MARKET,
                product=self.kite.PRODUCT_MIS,
                tag="BOT_ENTRY"
            )
        except Exception as e:
            logger.error(f"Entry Failed: {e}")
            return None

    def place_sl_order(self, symbol, side, qty, trigger_price):
        """Tries SL-M first, falls back to SL-LIMIT if blocked"""
        try:
            tx = self.kite.TRANSACTION_TYPE_SELL if side == "BUY" else self.kite.TRANSACTION_TYPE_BUY
            
            # Attempt 1: SL-M
            try:
                return self.kite.place_order(
                    tradingsymbol=symbol.replace("NSE:", ""),
                    exchange=self.kite.EXCHANGE_NSE,
                    transaction_type=tx,
                    quantity=qty,
                    variety=self.kite.VARIETY_REGULAR,
                    order_type=self.kite.ORDER_TYPE_SL_M,
                    product=self.kite.PRODUCT_MIS,
                    trigger_price=round(trigger_price, 1),
                    tag="BOT_SL"
                )
            except Exception as e:
                # Fallback Logic: If SL-M blocked, use SL-LIMIT
                if "InputException" in str(e) or "SL-M" in str(e):
                    logger.warning(f"SL-M blocked for {symbol}. Using SL-LIMIT.")
                    buffer = trigger_price * 0.01 
                    limit_price = trigger_price - buffer if tx == self.kite.TRANSACTION_TYPE_SELL else trigger_price + buffer
                    
                    return self.kite.place_order(
                        tradingsymbol=symbol.replace("NSE:", ""),
                        exchange=self.kite.EXCHANGE_NSE,
                        transaction_type=tx,
                        quantity=qty,
                        variety=self.kite.VARIETY_REGULAR,
                        order_type=self.kite.ORDER_TYPE_SL,
                        product=self.kite.PRODUCT_MIS,
                        price=round(limit_price, 1),
                        trigger_price=round(trigger_price, 1),
                        tag="BOT_SL_L"
                    )
                raise e

        except Exception as e:
            logger.error(f"SL Failed: {e}")
            return None

    def modify_order(self, order_id, new_trigger):
        try:
            self.kite.modify_order(
                variety=self.kite.VARIETY_REGULAR,
                order_id=order_id,
                trigger_price=round(new_trigger, 1)
            )
            return True
        except Exception as e:
            logger.error(f"Modify Failed: {e}")
            return False

    def cancel_order(self, order_id):
        try:
            self.kite.cancel_order(self.kite.VARIETY_REGULAR, order_id)
        except: pass

    def get_order_status(self, order_id):
        try:
            hist = self.kite.order_history(order_id)
            if hist: return hist[-1]['status']
        except: pass
        return "UNKNOWN"

