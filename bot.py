import asyncio
import yfinance as yf
import pandas as pd
import ta
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None

bot = Bot(token=TOKEN)

pair = "GC=F"   # الذهب العالمي

def analyze():
    data = yf.download(pair, interval="5m", period="1d", progress=False)

    if data is None or data.empty:
        return None

    close = data["Close"].squeeze()
    if close is None or len(close) < 50:
        return None

    price = float(close.iloc[-1])

    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    macd = ta.trend.MACD(close).macd_diff().iloc[-1]
    ema20 = ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]

    قوة = 50
    سبب = []

    if price > ema20:
        قوة += 10
        سبب.append("فوق EMA20")

    if price > ema50:
        قوة += 10
        سبب.append("فوق EMA50")

    if rsi > 55:
        قوة += 10
        سبب.append("RSI صاعد")

    if rsi < 45:
        قوة += 10
        سبب.append("RSI نازل")

    if macd > 0:
        قوة += 10
        سبب.append("زخم صاعد")

    if macd < 0:
        قوة += 10
        سبب.append("زخم هابط")

    if قوة < 60:
        return None

    if rsi > 55 and macd > 0 and price > ema20:
        نوع = "BUY"
        tp = price + 2
        sl = price - 1
        اتجاه = "صعود قوي"

    elif rsi < 45 and macd < 0 and price < ema20:
        نوع = "SELL"
        tp = price - 2
        sl = price + 1
        اتجاه = "هبوط قوي"

    else:
        return None

    رسالة = f"""
⚡ GOLD SCALPING SIGNAL

{نوع} GOLD 🪙
الدخول: {price:.2f}

🎯 الهدف: {tp:.2f}
🛑 الوقف: {sl:.2f}

📊 القوة: {قوة}%

🧠 التحليل:
- {اتجاه}
- {", ".join(سبب)}

📱 الدخول اختياري
"""
    return رسالة


async def main():
    global CHAT_ID

    updates = await bot.get_updates()
    if updates:
        CHAT_ID = updates[-1].message.chat_id

    print("GOLD BOT STARTED 🔥")

    while True:
        signal = analyze()
        if signal and CHAT_ID:
            await bot.send_message(chat_id=CHAT_ID, text=signal)

        await asyncio.sleep(300)  # كل 5 دقائق


asyncio.run(main())
