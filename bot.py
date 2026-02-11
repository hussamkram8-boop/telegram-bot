import asyncio
import yfinance as yf
import ta
import datetime
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None
bot = Bot(token=TOKEN)

pair = "GC=F"

# ===== وقت التداول =====
def trading_time():
    now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
    return 10 <= now.hour <= 23

# ===== قراءة رسائل =====
last_update_id = None

async def reply_updates():
    global CHAT_ID, last_update_id

updates = await bot.get_updates(timeout=10)

    for update in updates:
        last_update_id = update.update_id + 1

        if update.message:
            CHAT_ID = update.message.chat_id
            text = update.message.text.lower()

            if "/start" in text:
                await bot.send_message(CHAT_ID, "🔥 البوت شغال ويراقب الذهب")

            elif "حالة" in text:
                await bot.send_message(CHAT_ID, "🟢 البوت يعمل الآن")

            elif "تحليل" in text:
                await bot.send_message(CHAT_ID, "📊 السوق تحت المراقبة")

# ===== تحليل الذهب =====
def analyze():
    if not trading_time():
        return None

    data = yf.download(pair, interval="5m", period="1d", progress=False)

    if data is None or data.empty:
        return None

    close = data["Close"].squeeze()
    if len(close) < 50:
        return None

    price = float(close.iloc[-1])

    rsi = ta.momentum.RSIIndicator(close, 14).rsi().iloc[-1]
    ema20 = ta.trend.EMAIndicator(close, 20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(close, 50).ema_indicator().iloc[-1]

    confidence = 70

    if ema20 > ema50:
        confidence += 10
    if rsi > 55:
        confidence += 10

    if confidence < 85:
        return None

    if ema20 > ema50 and rsi > 55:
        side = "BUY 🟢"
        tp = price + 20
        sl = price - 10
    else:
        return None

    return f"""
👑 GOLD VIP SIGNAL

{side}
Entry: {price:.2f}

🎯 TP: {tp:.2f}
🛑 SL: {sl:.2f}

📊 Confidence: {confidence}%
"""

# ===== التشغيل =====
async def main():
    print("BOT STARTED")

    while True:
        await reply_updates()

        signal = analyze()
        if signal and CHAT_ID:
            await bot.send_message(chat_id=CHAT_ID, text=signal)

        await asyncio.sleep(300)

asyncio.run(main())
