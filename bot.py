import asyncio
import requests
import ta
import datetime
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None
bot = Bot(token=TOKEN)

# ===== الأزواج =====
pairs = {
    "XAUUSDT": "GOLD",
    "EURUSDT": "EURUSD",
    "GBPUSDT": "GBPUSD"
}

last_signal = {}

# ===== وقت التداول =====
def trading_time():
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
    return 9 <= now.hour <= 23

# ===== جلب بيانات من Binance =====
def get_binance(symbol, interval="15m", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()

    if not isinstance(data, list):
        return None

    closes = [float(candle[4]) for candle in data]
    return closes

# ===== قراءة رسائل التليجرام =====
async def reply_updates():
    global CHAT_ID
    updates = await bot.get_updates()

    for update in updates:
        if update.message:
            CHAT_ID = update.message.chat_id
            text = update.message.text.lower()

            if "/start" in text:
                await bot.send_message(chat_id=CHAT_ID,
                text="🔥 بوت VIP شغال — فقط ضربات قوية جداً")

            if "حالة" in text:
                await bot.send_message(chat_id=CHAT_ID,
                text="🟢 البوت يعمل ويراقب أقوى الفرص فقط")

# ===== التحليل =====
def analyze(pair_code, pair_name):

    if not trading_time():
        return None

    try:
        h1 = get_binance(pair_code, "1h", 200)
        m15 = get_binance(pair_code, "15m", 200)
    except:
        return None

    if not h1 or not m15:
        return None

    if len(h1) < 60 or len(m15) < 60:
        return None

    price = float(m15[-1])

    # تحويل لقائمة pandas
    import pandas as pd
    close_h1 = pd.Series(h1)
    close_m15 = pd.Series(m15)

    # مؤشرات
    rsi_h1 = ta.momentum.RSIIndicator(close_h1, 14).rsi().iloc[-1]
    ema20_h1 = ta.trend.EMAIndicator(close_h1, 20).ema_indicator().iloc[-1]
    ema50_h1 = ta.trend.EMAIndicator(close_h1, 50).ema_indicator().iloc[-1]

    rsi_15 = ta.momentum.RSIIndicator(close_m15, 14).rsi().iloc[-1]
    ema20_15 = ta.trend.EMAIndicator(close_m15, 20).ema_indicator().iloc[-1]
    ema50_15 = ta.trend.EMAIndicator(close_m15, 50).ema_indicator().iloc[-1]

    confidence = 0
    reason = []

    if ema20_h1 > ema50_h1:
        confidence += 30
        reason.append("ترند صاعد قوي H1")

    if rsi_h1 > 55:
        confidence += 20
        reason.append("زخم شراء قوي")

    if ema20_15 > ema50_15:
        confidence += 20
        reason.append("تقاطع صاعد M15")

    if rsi_15 > 60:
        confidence += 20
        reason.append("RSI قوي")

    if price > ema20_15:
        confidence += 10

    if confidence < 85:
        return None

    signal_type = "BUY 🟢"
    tp = price * 1.005
    sl = price * 0.997

    key = pair_name + signal_type
    if key in last_signal:
        last_price = last_signal[key]
        if abs(price - last_price) < price * 0.0015:
            return None

    last_signal[key] = price

    msg = f"""
🔥 VIP STRONG SIGNAL

الزوج: {pair_name}
النوع: {signal_type}

الدخول: {price:.5f}

🎯 الهدف: {tp:.5f}
🛑 الوقف: {sl:.5f}

قوة الصفقة: {confidence}%
"""
    return msg

# ===== التشغيل =====
async def main():
    print("VIP BOT RUNNING 🔥")

    while True:
        await reply_updates()

        for code, name in pairs.items():
            signal = analyze(code, name)
            if signal and CHAT_ID:
                await bot.send_message(chat_id=CHAT_ID, text=signal)

        await asyncio.sleep(600)

asyncio.run(main())
