import asyncio
import yfinance as yf
import ta
import datetime
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None
bot = Bot(token=TOKEN)

pair = "GC=F"

# ===== إعداد VIP =====
MAX_SIGNALS_PER_DAY = 5
MIN_CONFIDENCE = 85

signals_today = 0
last_day = datetime.date.today()

# ===== وقت التداول لندن + أمريكا =====
def trading_time():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)  # توقيت العراق
    hour = now.hour
    if 10 <= hour <= 23:
        return True
    return False

# ===== أوقات الأخبار =====
def news_time():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    h = now.hour
    m = now.minute

    news_slots = [
        (15,30),
        (17,0),
        (21,30)
    ]

    for nh, nm in news_slots:
        if h == nh and abs(m-nm) <= 20:
            return True
    return False

# ===== الرد على الرسائل =====
async def reply_updates():
    global CHAT_ID
    updates = await bot.get_updates()

    for update in updates:
        if update.message:
            CHAT_ID = update.message.chat_id
            text = update.message.text.lower()

            if "start" in text or "هلا" in text:
                await bot.send_message(CHAT_ID, "🔥 GOLD VIP BOT ACTIVE")

            elif "وضع" in text:
                await bot.send_message(CHAT_ID, "👑 VIP SNIPER MODE")

            elif "سعر" in text:
                data = yf.download(pair, period="1d", interval="1m")
                price = float(data["Close"].iloc[-1])
                await bot.send_message(CHAT_ID, f"💰 سعر الذهب: {price}")

# ===== تحليل VIP =====
def analyze():
    global signals_today, last_day

    if not trading_time():
        return None

    if news_time():
        return None

    # تصفير يومي
    if datetime.date.today() != last_day:
        signals_today = 0
        last_day = datetime.date.today()

    if signals_today >= MAX_SIGNALS_PER_DAY:
        return None

    data = yf.download(pair, interval="5m", period="1d", progress=False)
    if data.empty or len(data) < 60:
        return None

    close = data["Close"]
    price = float(close.iloc[-1])

    rsi = ta.momentum.RSIIndicator(close, 14).rsi().iloc[-1]
    ema20 = ta.trend.EMAIndicator(close, 20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(close, 50).ema_indicator().iloc[-1]

    # دعم ومقاومة
    high = data["High"].rolling(20).max().iloc[-1]
    low = data["Low"].rolling(20).min().iloc[-1]

    if abs(price - high) < 3:
        return None
    if abs(price - low) < 3:
        return None

    confidence = 75
    reasons = []

    if ema20 > ema50:
        confidence += 10
        reasons.append("ترند صاعد")
    else:
        confidence -= 5

    if rsi > 55:
        confidence += 10
        reasons.append("RSI إيجابي")

    if rsi < 45:
        confidence += 10
        reasons.append("RSI سلبي")

    if confidence < MIN_CONFIDENCE:
        return None

    # ===== دخول =====
    sniper = False

    if ema20 > ema50 and rsi > 60:
        side = "BUY 🟢"
        tp = price + 25
        sl = price - 12
        trend = "زخم صاعد قوي"
        if confidence >= 95:
            sniper = True

    elif ema20 < ema50 and rsi < 40:
        side = "SELL 🔴"
        tp = price - 25
        sl = price + 12
        trend = "زخم هابط قوي"
        if confidence >= 95:
            sniper = True
    else:
        return None

    signals_today += 1

    if sniper:
        header = "🚨 GOLD SNIPER ENTRY 🚨"
    else:
        header = "👑 GOLD VIP SIGNAL"

    return f"""
{header}

{side}
Entry: {price:.2f}

🎯 TP: {tp:.2f}
🛑 SL: {sl:.2f}

📊 Confidence: {confidence}%

🧠 Analysis:
- {trend}
- {" | ".join(reasons)}

📡 VIP BOT
"""

# ===== التشغيل =====
async def main():
    global start_sent, CHAT_ID

    print("🔥 GOLD VIP SNIPER BOT STARTED")

    while True:
        await reply_updates()

        # ارسال رسالة التشغيل مرة وحدة فقط
        if CHAT_ID and not start_sent:
            await bot.send_message(chat_id=CHAT_ID, text="🔥 GOLD VIP BOT ACTIVE")
            start_sent = True

        signal = analyze()
        if signal and CHAT_ID:
            await bot.send_message(chat_id=CHAT_ID, text=signal)

        await asyncio.sleep(300)
