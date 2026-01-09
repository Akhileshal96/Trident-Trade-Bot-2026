import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Kite
    KITE_API_KEY: str = os.getenv("KITE_API_KEY", "")
    KITE_API_SECRET: str = os.getenv("KITE_API_SECRET", "")
    KITE_ACCESS_TOKEN: str = os.getenv("KITE_ACCESS_TOKEN", "")
    
    # Telegram
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID", 0))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: int = int(os.getenv("TELEGRAM_CHAT_ID", 0))
    
    # Auth List
    _allowed = os.getenv("TG_ALLOWED_IDS", "")
    ALLOWED_TELEGRAM_IDS: list = [int(x) for x in _allowed.split()] if _allowed else

    # Risk & Capital
    TRADING_MODE: str = os.getenv("TRADING_MODE", "LIVE")
    CAPITAL_MODE: str = os.getenv("CAPITAL_MODE", "LIVE")
    CAPITAL: float = float(os.getenv("CAPITAL", 50000))
    MARGIN_UTILIZATION: float = float(os.getenv("MARGIN_UTILIZATION", 1.0))
    RISK_PER_TRADE: float = float(os.getenv("RISK_PER_TRADE", 500))
    MAX_OPEN_POSITIONS: int = int(os.getenv("MAX_OPEN_POSITIONS", 1))
    
    # Strategy
    TIMEFRAME: str = os.getenv("TIMEFRAME", "3minute")
    SQUARE_OFF_TIME: str = os.getenv("SQUARE_OFF_TIME", "15:15")
    USE_TRAILING_SL: bool = os.getenv("USE_TRAILING_SL", "True").lower() == "true"
    TRAILING_PCT: float = float(os.getenv("TRAILING_PCT", 0.005))

    # Scanner Pool
    SYMBOLS: list = os.getenv("SYMBOLS", "").split(",")

settings = Settings()

