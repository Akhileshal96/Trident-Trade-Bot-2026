from datetime import datetime, time
import pytz
from bot.config import settings

IST = pytz.timezone('Asia/Kolkata')

def get_current_time(): return datetime.now(IST)

def is_market_open():
    now = get_current_time().time()
    return time(9, 15) <= now <= time(15, 30)

def is_square_off_time():
    now = get_current_time().time()
    h, m = map(int, settings.SQUARE_OFF_TIME.split(":"))
    return now >= time(h, m)

def is_entry_allowed():
    now = get_current_time().time()
    return time(9, 15) <= now <= time(14, 50)

