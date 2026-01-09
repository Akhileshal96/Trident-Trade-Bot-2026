# Trident-Trade-Bot-2026

# 📈 Zerodha Algorithmic Trading Bot (V5.0 - Max Profit Edition)

A high-performance, asynchronous algorithmic trading bot built for the **Zerodha Kite Connect API**. This system is designed for **Aggressive Momentum Trading** with self-healing capabilities, live market scanning, and full control via Telegram.

![Status](https://img.shields.io/badge/Status-Live-green) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Strategy](https://img.shields.io/badge/Strategy-Aggressive%20Momentum-red)

## 🔥 Key Features (Max Profit Edition)

* **🚀 Aggressive Strategy:** Runs on a **3-minute timeframe** to catch breakouts early.
* **💰 Dynamic Capital:** Automatically detects your live Zerodha wallet balance and uses **100% margin utilization** for maximum gains.
* **🛡️ Trailing Stop Loss:** Doesn't just book fixed profits. It **trails price by 0.5%**, allowing winning trades to run indefinitely until the trend reverses.
* **📡 Auto-Scanner:** Automatically scans the **Nifty 50** at market open to find the top 3 high-volatility movers of the day.
* **📱 Telegram Command Center:** Full control from your phone. View logs, export trade history to Excel, and blacklist stocks.
* **❤️ Self-Healing:** If your Kite Access Token expires, the bot alerts you on Telegram. You can renew it instantly via chat without logging into the server.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
* Python 3.9 or higher
* Zerodha Kite Connect API Account
* Telegram Bot Token (via BotFather)

### 2. Clone Repository
```bash
git clone [https://github.com/yourusername/zerodha_bot_v5.git](https://github.com/yourusername/zerodha_bot_v5.git)
cd zerodha_bot_v5
