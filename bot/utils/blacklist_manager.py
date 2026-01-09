import json
import os
from bot.utils.logger import logger

FILE = "data/blacklist.json"

class BlacklistManager:
    def __init__(self):
        if not os.path.exists("data"): os.makedirs("data")
        if not os.path.exists(FILE): 
            with open(FILE, "w") as f: json.dump(, f)

    def get_blacklist(self):
        try:
            with open(FILE, "r") as f: return set(json.load(f))
        except: return set()

    def add_stock(self, sym):
        lst = list(self.get_blacklist())
        if sym not in lst:
            lst.append(sym)
            with open(FILE, "w") as f: json.dump(lst, f)
            return True
        return False

    def remove_stock(self, sym):
        lst = list(self.get_blacklist())
        if sym in lst:
            lst.remove(sym)
            with open(FILE, "w") as f: json.dump(lst, f)
            return True
        return False

