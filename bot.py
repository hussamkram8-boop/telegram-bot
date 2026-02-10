import asyncio
import yfinance as yf
import pandas as pd
import ta
from telegram import Bot

TOKEN = "8248315922:AAGcgFTRbtffoJOUr_WLbyc3JbttFxQEZk4"
CHAT_ID = None

pairs = [
"EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X",
"USDCAD=X","EURJPY=X","GBPJPY=X","AUDJPY=X"
]

bot = Bot(token=TOKEN)

def analyze(pair, tf):
    data = yf.download(pair, interval=tf, period="1d", progress=False)
    if data is None or data.empty:
        return None

    close = data["Close"].squeeze()
    if close is None or len(close) < 2:
        return None

    price = close.iloc[-1]

    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    macd = ta.trend.MACD(close).macd_diff().iloc[-1]
    ema20 = ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1]
    ema50 = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]

    قوة = 0
    سبب = []

    if price > ema20:
        قوة += 15
        سبب.append("فوق EMA20")
    if price > ema50:
        قوة += 15
        سبب.append("فوق EMA50")
    if rsi < 35:
        قوة += 20
        سبب.append("تشبع بيع")
    if rsi > 65:
        قوة += 20
        سبب.append("تشبع شراء")
    if macd > 0:
        قوة += 15
        سبب.append("MACD صاعد")
    if macd < 0:
        قوة += 15
        سبب.append("MACD هابط")

    if قوة < 60:
        return None

    if rsi < 40 and macd > 0 and price > ema20:
        نوع = "شراء BUY"
        tp = price + 0.004
        sl = price - 0.002
    elif rsi > 60 and macd < 0 and price < ema20:
        نوع = "بيع SELL"
        tp = price - 0.004
        sl = price + 0.002
    else:
        return None

    رسالة = f"""
👑 صفقة احتراف

الزوج: {pair.replace("=X","")}
الفريم: {tf}
النوع: {نوع}

الدخول: {price:.5f}
الهدف: {tp:.5f}
الوقف: {sl:.5f}

قوة الصفقة: {قوة}%

التحليل:
{", ".join(سبب)}
"""
    return رسالة

async def main():
    global CHAT_ID
    updates = await bot.get_updates()
    if updates:
        CHAT_ID = updates[-1].message.chat_id

    print("البوت الاحترافي يعمل 🔥")

    while True:
        for pair in pairs:
            for tf in ["5m","15m"]:
                res = analyze(pair, tf)
                if res and CHAT_ID:
                    await bot.send_message(chat_id=CHAT_ID, text=res)

        await asyncio.sleep(900)

asyncio.run(main())
