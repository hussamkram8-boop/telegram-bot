import asyncio
import yfinance as yf
import pandas as pd
import ta
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None

pairs = [
"EURUSD=X",
"GBPUSD=X",
"USDJPY=X",
"AUDUSD=X",
"USDCAD=X",
"EURJPY=X",
"GBPJPY=X"
]

bot = Bot(token=TOKEN)

def analyze_pair(pair):
    data = yf.download(pair, interval="5m", period="1d", progress=False)

    if data is None or data.empty:
        return None

    close = data["Close"].squeeze()

    rsi = ta.momentum.RSIIndicator(close=close).rsi().iloc[-1]
    macd = ta.trend.MACD(close=close).macd_diff().iloc[-1]
    ema20 = ta.trend.EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]

    price = close.iloc[-1]

    signal = "انتظار"
    reason = ""

    if rsi < 30 and macd > 0 and price > ema20:
        signal = "BUY"
        reason = "تشبع بيع + صعود MACD + فوق EMA"
    elif rsi > 70 and macd < 0 and price < ema20:
        signal = "SELL"
        reason = "تشبع شراء + هبوط MACD + تحت EMA"

    if signal == "انتظار":
        return None

    tp = price + 0.005 if signal=="BUY" else price - 0.005
    sl = price - 0.003 if signal=="BUY" else price + 0.003

    msg = f"""
🔥 فرصة تداول

الزوج: {pair.replace("=X","")}
الاشارة: {signal}

الدخول: {price:.5f}
الهدف: {tp:.5f}
الوقف: {sl:.5f}

السبب: {reason}
RSI: {rsi:.1f}
"""
    return msg

async def main():
    global CHAT_ID
    updates = await bot.get_updates()
    if updates:
        CHAT_ID = updates[-1].message.chat_id

    print("البوت يعمل الآن 🔥")

    while True:
        for pair in pairs:
            res = analyze_pair(pair)
            if res and CHAT_ID:
                await bot.send_message(chat_id=CHAT_ID, text=res)

        await asyncio.sleep(900)

asyncio.run(main())
