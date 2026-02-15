import asyncio
import yfinance as yf
import ta
import datetime
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None
bot = Bot(token=TOKEN)

pairs = {
    "XAUUSD=X": "GOLD",
    "EURUSD=X": "EURUSD",
    "GBPUSD=X": "GBPUSD"
}

last_signal = {}

# ===== وقت التداول =====
def trading_time():
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
    return 9 <= now.hour <= 23

# ===== قراءة الرسائل =====
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

# ===== التحليل القوي =====
def analyze(pair_code, pair_name):

    if not trading_time():
        return None

    try:
        h1 = yf.download(pair_code, interval="1h", period="7d", progress=False)
        m15 = yf.download(pair_code, interval="15m", period="2d", progress=False)
    except:
        return None

    if h1.empty or m15.empty:
        return None

    close_h1 = h1["Close"].squeeze()
    close_m15 = m15["Close"].squeeze()

    if len(close_h1) < 60 or len(close_m15) < 60:
        return None

    price = float(close_m15.iloc[-1])

    # مؤشرات الساعة
    rsi_h1 = ta.momentum.RSIIndicator(close_h1, 14).rsi().iloc[-1]
    ema20_h1 = ta.trend.EMAIndicator(close_h1, 20).ema_indicator().iloc[-1]
    ema50_h1 = ta.trend.EMAIndicator(close_h1, 50).ema_indicator().iloc[-1]

    # مؤشرات 15
    rsi_15 = ta.momentum.RSIIndicator(close_m15, 14).rsi().iloc[-1]
    ema20_15 = ta.trend.EMAIndicator(close_m15, 20).ema_indicator().iloc[-1]
    ema50_15 = ta.trend.EMAIndicator(close_m15, 50).ema_indicator().iloc[-1]

    confidence = 0
    reason = []

    # ترند عام
    if ema20_h1 > ema50_h1:
        confidence += 30
        reason.append("ترند صاعد قوي H1")

    if rsi_h1 > 55:
        confidence += 20
        reason.append("زخم شراء قوي")

    # دخول قوي
    if ema20_15 > ema50_15:
        confidence += 20
        reason.append("تقاطع صاعد M15")

    if rsi_15 > 60:
        confidence += 20
        reason.append("دخول مؤكد RSI")

    if price > ema20_15:
        confidence += 10

    # فقط ضربات قوية جداً
    if confidence < 85:
        return None

    signal_type = "BUY 🟢"
    tp = price * 1.005
    sl = price * 0.997

    # منع التكرار
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

        await asyncio.sleep(600)  # كل 10 دقائق فقط

asyncio.run(main())
