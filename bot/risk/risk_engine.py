from bot.config import settings

class RiskEngine:
    def calculate_quantity(self, entry, sl, capital):
        usable = capital * settings.MARGIN_UTILIZATION
        risk_per_share = abs(entry - sl)
        if risk_per_share == 0: return 0
        
        qty_risk = settings.RISK_PER_TRADE / risk_per_share
        qty_cap = usable / (entry / 5) # 5x Leverage
        
        return int(min(qty_risk, qty_cap))

