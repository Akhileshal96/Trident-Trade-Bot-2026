import time
from bot.utils.logger import logger, log_trade

class OrderManager:
    def __init__(self, broker):
        self.broker = broker
        self.active_trades = {}

    def place_entry(self, symbol, side, qty, sl_price):
        logger.info(f"🚀 ENTRY: {symbol} {side} Qty: {qty}")
        entry_id = self.broker.place_market_order(symbol, side, qty)
        if not entry_id: return False

        # Confirm Fill
        filled, avg_price = False, 0.0
        for _ in range(5):
            status = self.broker.get_order_status(entry_id)
            if status == "COMPLETE":
                filled = True
                avg_price = self.broker.get_ltp(symbol)
                break
            time.sleep(1)

        if not filled:
            logger.error(f"⚠️ STUCK: {symbol}")
            return False

        # Place SL
        sl_id = self.broker.place_sl_order(symbol, side, qty, sl_price)
        self.active_trades[symbol] = {
            "sl_id": sl_id, "qty": qty, "side": side, 
            "entry": avg_price, "current_sl": sl_price
        }
        log_trade(symbol, side, qty, avg_price, "ENTRY")
        return True

    def modify_sl(self, symbol, new_sl):
        if symbol not in self.active_trades: return
        trade = self.active_trades[symbol]
        
        if trade.get('sl_id'):
            success = self.broker.modify_order(trade['sl_id'], new_sl)
            if success:
                logger.info(f"⚡ Trailed SL {symbol}: {trade['current_sl']} -> {new_sl}")
                trade['current_sl'] = new_sl

    def close_all_positions(self):
        logger.warning("🚨 Closing ALL Positions...")
        for symbol, data in list(self.active_trades.items()):
            side = data['side']
            qty = data['qty']
            exit_side = "SELL" if side == "BUY" else "BUY"
            self.broker.place_market_order(symbol, exit_side, qty)
            if data.get('sl_id'): self.broker.cancel_order(data['sl_id'])
            del self.active_trades[symbol]

    def check_sl_hit(self, symbol):
        if symbol not in self.active_trades: return False
        sl_id = self.active_trades[symbol].get('sl_id')
        if sl_id and self.broker.get_order_status(sl_id) == "COMPLETE":
            del self.active_trades[symbol]
            return True
        return False

