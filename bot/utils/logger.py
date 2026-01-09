import sys
from loguru import logger
from datetime import datetime

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
logger.add("bot.log", rotation="1 day", retention="7 days")
logger.add("logs/trades.csv", filter=lambda r: "TRADE_CSV" in r["extra"], format="{message}")

def log_trade(symbol, side, qty, price, type):
    logger.bind(TRADE_CSV=True).info(f"{datetime.now()},{symbol},{side},{qty},{price},{type}")

