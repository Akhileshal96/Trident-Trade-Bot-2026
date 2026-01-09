import asyncio
import sys
import os
import io
import pandas as pd
from collections import deque
from telethon import TelegramClient, events
from dotenv import set_key
from datetime import datetime, timedelta

from bot.config import settings
from bot import globals
from bot.broker.zerodha_client import ZerodhaClient
from bot.execution.order_manager import OrderManager
from bot.risk.risk_engine import RiskEngine
from bot.strategy.ema_strategy import Strategy
from bot.analysis.scanner import MarketScanner
from bot.data.market_data import MarketData
from bot.utils import time_utils
from bot.utils.logger import logger
from bot.utils.token_manager import TokenManager
from bot.utils.blacklist_manager import BlacklistManager

# --- INIT ---
bot = TelegramClient('bot_session', settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
broker = ZerodhaClient() 
order_manager = OrderManager(broker)
risk_engine = RiskEngine()
blacklist_mgr = BlacklistManager()

def is_authorized(sender_id):
    # Check if sender is in allowed list OR if msg is from allowed Group
    return sender_id in settings.ALLOWED_TELEGRAM_IDS

# --- COMMANDS ---

@bot.on(events.NewMessage(pattern='/help'))
async def help_cmd(event):
    if not is_authorized(event.chat_id): return
    msg = (
        "🤖 **MAX PROFIT BOT COMMANDS**\n\n"
        "📊 `/status` - PnL & Positions\n"
        "📜 `/logs` - View last 20 logs\n"
        "📂 `/export` - Download Excel logs\n"
        "🚫 `/exclude SYMBOL` - Blacklist a stock\n"
        "✅ `/include SYMBOL` - Un-blacklist a stock\n"
        "🔄 `/renewtoken TOKEN` - Update API Token"
    )
    await event.respond(msg)

@bot.on(events.NewMessage(pattern='/logs'))
async def logs_cmd(event):
    if not is_authorized(event.chat_id): return
    try:
        with open("bot.log", "r") as f:
            lines = deque(f, maxlen=20)
        await event.respond(f"**LOGS:**\n`{''.join(lines)}`")
    except: await event.respond("No logs found.")

@bot.on(events.NewMessage(pattern='/export'))
async def export_cmd(event):
    if not is_authorized(event.chat_id): return
    await event.respond("⏳ Generating Excel...")
    try:
        df = pd.read_csv("logs/trades.csv", names=)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        buffer.name = f"Trades_{datetime.now().date()}.xlsx"
        await event.client.send_file(event.chat_id, buffer)
    except: await event.respond("No trades to export.")

@bot.on(events.NewMessage(pattern='/exclude (.+)'))
async def exclude_cmd(event):
    if not is_authorized(event.chat_id): return
    sym = event.pattern_match.group(1).upper().strip()
    if blacklist_mgr.add_stock(sym):
        if sym in globals.SELECTED_SYMBOLS: globals.SELECTED_SYMBOLS.remove(sym)
        await event.respond(f"🚫 {sym} added to blacklist.")
    else: await event.respond("Already excluded.")

@bot.on(events.NewMessage(pattern='/include (.+)'))
async def include_cmd(event):
    if not is_authorized(event.chat_id): return
    sym = event.pattern_match.group(1).upper().strip()
    if blacklist_mgr.remove_stock(sym):
        await event.respond(f"✅ {sym} removed from blacklist.")

@bot.on(events.NewMessage(pattern='/renewtoken (.+)'))
async def renew_cmd(event):
    if not is_authorized(event.chat_id): return
    token = event.pattern_match.group(1).strip()
    settings.KITE_ACCESS_TOKEN = token
    broker.kite.set_access_token(token)
    set_key(".env", "KITE_ACCESS_TOKEN", token)
    await event.respond("✅ Token Updated! Bot resuming.")

@bot.on(events.NewMessage(pattern='/status'))
async def status_cmd(event):
    if not is_authorized(event.chat_id): return
    msg = f"🟢 **ONLINE**\nTrades: {len(order_manager.active_trades)}\nTracking: `{globals.SELECTED_SYMBOLS}`"
    await event.respond(msg)

# --- TRADING ENGINE ---

async def trading_loop():
    logger.info("⏳ Initializing Engine...")

    # 1. SMART STARTUP
    token_mgr = TokenManager()
    while True:
        kite = token_mgr.validate_token()
        if kite:
            broker.kite = kite 
            break
        logger.warning("⚠️ Token Invalid.")
        if sys.stdin.isatty():
            print(f"Login: {broker.kite.login_url()}")
            t = input("Token: ").strip()
            # If request token
            if len(t) < 32:
                data = broker.kite.generate_session(t, api_secret=settings.KITE_API_SECRET)
                t = data["access_token"]
            
            settings.KITE_ACCESS_TOKEN = t
            set_key(".env", "KITE_ACCESS_TOKEN", t)
        else:
            await bot.send_message(settings.TELEGRAM_CHAT_ID, "🚨 **Token Expired!** Reply `/renewtoken <token>`")
            await asyncio.sleep(60)

    # 2. RUN SCANNER
    scanner = MarketScanner(broker)
    globals.SELECTED_SYMBOLS = scanner.scan_and_select(top_n=3)
    await bot.send_message(settings.TELEGRAM_CHAT_ID, f"☀️ **Market Open!**\nTargeting: `{globals.SELECTED_SYMBOLS}`")

    market_data = MarketData(broker)
    strategy = Strategy()

    # 3. MAIN LOOP
    while not globals.STOP_BOT:
        try:
            if time_utils.is_square_off_time():
                order_manager.close_all_positions()
                await bot.send_message(settings.TELEGRAM_CHAT_ID, "🏁 Day End. Positions Closed.")
                break

            if not time_utils.is_market_open():
                await asyncio.sleep(60)
                continue

            for symbol in globals.SELECTED_SYMBOLS:
                # TRAILING SL
                if symbol in order_manager.active_trades:
                    trade = order_manager.active_trades[symbol]
                    if trade['side'] == 'BUY':
                        ltp = broker.get_ltp(symbol)
                        new_sl = ltp - (ltp * settings.TRAILING_PCT)
                        if new_sl > trade['current_sl']:
                            order_manager.modify_sl(symbol, new_sl)
                    order_manager.check_sl_hit(symbol)
                    continue

                # NEW ENTRY
                df = market_data.get_ohlc(symbol, settings.TIMEFRAME)
                if df is None: continue

                signal, price = strategy.analyze(df)
                
                if signal == "BUY":
                    cap = settings.CAPITAL
                    if settings.CAPITAL_MODE == "LIVE":
                        m = broker.get_available_margin()
                        if m: cap = m
                    
                    sl_price = price * (1 - settings.TRAILING_PCT)
                    qty = risk_engine.calculate_quantity(price, sl_price, cap)
                    
                    if qty > 0:
                        if order_manager.place_entry(symbol, signal, qty, sl_price):
                            await bot.send_message(settings.TELEGRAM_CHAT_ID, f"🚀 **BUY** {symbol} @ {price} | Qty: {qty}")

            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Loop Error: {e}")
            await asyncio.sleep(5)

async def main():
    await bot.start(bot_token=settings.TELEGRAM_BOT_TOKEN)
    bot.loop.create_task(trading_loop())
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

