from bot.config import settings
from kiteconnect import KiteConnect
from bot.utils.logger import logger

class TokenManager:
    def __init__(self):
        self.api_key = settings.KITE_API_KEY
        self.access_token = settings.KITE_ACCESS_TOKEN

    def validate_token(self):
        try:
            k = KiteConnect(api_key=self.api_key)
            k.set_access_token(self.access_token)
            k.profile()
            return k
        except: return None
    
    def update_env_file(self, new_token):
        pass

