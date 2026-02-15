import asyncio
import yfinance as yf
import ta
import datetime
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None
bot = Bot(token=TOKEN)

pairs = {
    "GC=F": "GOLD",
    "EURUSD=X": "EURUSD",
    "GBPUSD=X": "GBPUSD"
}

last_signal = {}

# ===== هل السوق مفتوح =====
def market_open():
    now = datetime.datetime.utcnow()
    # السبت =5 الاحد=6
    if now.weekday() == 5:
        return False
    if now.weekday() == 6 and now.hour < 22:
        return False
    return True

# ===== الرد على الرسائل =====
async def reply_updates():
    global CHAT_ID
    updates = await bot.get_updates()

    for update in updates:
        if update.message:
            CHAT_ID = update.message.chat_id
            text = update.message.text.lower()

            if "/start" in text:
                await bot.send_message(chat_id=CHAT_ID,
                text="🔥 بوت VIP يعمل ويراقب الذهب واليورو والباوند")

            elif "حالة" in text:
                await bot.send_message(chat_id=CHAT_ID,
                text="🟢 البوت يعمل ويراقب الفرص القوية فقط")

# ===== التحليل =====
def analyze(pair_code, pair_name):

    if not market_open():
        return None

    try:
        h1 = yf.download(pair_code, interval="1h", period="5d", progress=False)
        m15 = yf.download(pair_code, interval="15m", period="1d", progress=False)
    except:
        return None

    if h1.empty or m15.empty:
        return None

    close_h1 = h1["Close"].squeeze()
    close_m15 = m15["Close"].squeeze()

    if len(close_h1) < 50 or len(close_m15) < 50:
        return None

    price = float(close_m15.iloc[-1])

    # مؤشرات الساعة
    rsi_h1 = ta.momentum.RSIIndicator(close_h1, 14).rsi().iloc[-1]
    ema20_h1 = ta.trend.EMAIndicator(close_h1, 20).ema_indicator().iloc[-1]
    ema50_h1 = ta.trend.EMAIndicator(close_h1, 50).ema_indicator().iloc[-1]

    # مؤشرات 15
    rsi_15 = ta.momentum.RSIIndicator(close_m15, 14).rsi().iloc[-1]
    ema20_15 = ta.trend.EMAIndicator(close_m15, 20).ema_indicator().iloc[-1]

    confidence = 0
    reason = []

    # ترند عام
    if ema20_h1 > ema50_h1:
        confidence += 35
        reason.append("ترند صاعد فريم ساعة")

    if rsi_h1 > 55:
        confidence += 25
        reason.append("زخم شراء قوي")

    # دخول
    if price > ema20_15:
        confidence += 20
        reason.append("السعر فوق متوسط 15")

    if rsi_15 > 55:
        confidence += 20
        reason.append("تأكيد دخول")

    if confidence < 85:
        return None

    signal_type = "شراء BUY 🟢"
    tp = price * 1.004
    sl = price * 0.997

    # منع التكرار
    key = pair_name + signal_type
    if key in last_signal:
        old = last_signal[key]
        if abs(price - old) < price * 0.001:
            return None

    last_signal[key] = price

    message = f"""
🔥 إشارة VIP قوية

الزوج: {pair_name}
النوع: {signal_type}

منطقة الدخول: {price:.5f}

🎯 الهدف: {tp:.5f}
🛑 الوقف: {sl:.5f}

قوة الصفقة: {confidence}%

التحليل:
{", ".join(reason)}
"""
    return message

# ===== التشغيل =====
async def main():
    print("VIP BOT RUNNING 🔥")

    while True:
        await reply_updates()

        if market_open():
            for code, name in pairs.items():
                signal = analyze(code, name)
                if signal and CHAT_ID:
                    await bot.send_message(chat_id=CHAT_ID, text=signal)

        await asyncio.sleep(900)

asyncio.run(main())
