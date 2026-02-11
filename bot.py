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
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    if 10 <= now.hour <= 23:
        return True
    return False

# ===== ردود البوت =====
last_update_id = None

async def reply_updates():
    global CHAT_ID, last_update_id

    updates = await bot.get_updates(offset=last_update_id, timeout=10)

    for update in updates:
        last_update_id = update.update_id + 1

        if update.message:
            chat_id = update.message.chat_id
            CHAT_ID = chat_id
            text = update.message.text.lower()

            if "/start" in text or "هلا" in text:
                await bot.send_message(chat_id, "🔥 البوت شغال ويراقب الذهب")

            elif "حالة" in text or "status" in text:
                await bot.send_message(chat_id, "🟢 البوت يعمل ويحلل الذهب الآن")

            elif "تحليل" in text:
                await bot.send_message(chat_id, "📊 السوق تحت المراقبة — أي فرصة قوية راح توصلك")

            elif "سعر" in text:
                data = yf.download(pair, period="1d", interval="1m")
                price = float(data["Close"].iloc[-1])
                await bot.send_message(chat_id, f"💰 سعر الذهب الآن: {price}")

# ===== تحليل =====
def analyze():
    if not trading_time():
        return None

    data = yf.download(pair, interval="5m", period="1d", progress=False)
    if data.empty:
        return None

    close = data["Close"]
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
