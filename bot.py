from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf
import pandas as pd
import ta

import os
TOKEN = os.environ.get("TOKEN")

TIMEFRAMES = {
    "M5": "5m",
    "M15": "15m"
}

def analyze_market(symbol, tf):
    if tf not in TIMEFRAMES:
        return "❌ الفريم غير مدعوم (المتاح: M5 / M15)"

    pair = symbol + "=X"
    interval = TIMEFRAMES[tf]

    data = yf.download(pair, period="1d", interval=interval, progress=False)

    if data.empty or len(data) < 20:
        return "❌ لا توجد بيانات كافية حالياً"

    # تنظيف الأعمدة
    data = data.reset_index()

    close = data["Close"]
    open_ = data["Open"]
    high = data["High"]
    low = data["Low"]

    price = round(close.iloc[-1], 5)

    # RSI
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]

    # ATR
    atr = ta.volatility.AverageTrueRange(
        high=high, low=low, close=close, window=14
    ).average_true_range().iloc[-1]

    atr = round(atr, 5)

    if atr < 0.0005:
        return "⚠️ السوق ضعيف (ATR منخفض)\n❌ لا يُنصح بالدخول"

    # اتجاه RSI
    if rsi < 40:
        decision = "SELL 🔴"
        direction = "هابط"
    elif rsi > 60:
        decision = "BUY 🟢"
        direction = "صاعد"
    else:
        return f"⚠️ السوق متذبذب\nRSI = {round(rsi,2)}\n❌ لا توجد إشارة واضحة"

    # تأكيد الشمعة
    candle_ok = False
    if decision.startswith("SELL") and close.iloc[-1] < open_.iloc[-1]:
        candle_ok = True
    if decision.startswith("BUY") and close.iloc[-1] > open_.iloc[-1]:
        candle_ok = True

    if not candle_ok:
        return (
            f"⚠️ تعارض بالإشارة\n"
            f"RSI: {round(rsi,2)} ({decision})\n"
            f"❌ الشمعة غير مؤكِّدة\n"
            f"📌 تحليل فقط"
        )

    # TP / SL
    if decision.startswith("SELL"):
        sl = price + atr
        tp = price - (atr * 2)
    else:
        sl = price - atr
        tp = price + (atr * 2)

    sl = round(sl, 5)
    tp = round(tp, 5)

    return f"""
📊 {symbol} - {tf}

📉 الاتجاه: {direction}
🎯 القرار: {decision}

💰 السعر الحالي: {price}
📈 RSI: {round(rsi,2)}
🌊 ATR: {atr}

🧠 سبب الدخول:
- RSI قوي
- شمعة مؤكِّدة
- زخم مناسب

🎯 TP: {tp}
🛑 SL: {sl}

⚠️ القرار النهائي لك
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 أهلاً بك!\n\n"
        "الأوامر:\n"
        "/analyze GBPUSD M5\n"
        "/analyze GBPUSD M15\n\n"
        "⛔ M1 غير مدعوم\n"
        "🧠 التحليل ذكي + فلترة قوية"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].upper()
        tf = context.args[1].upper()
    except:
        await update.message.reply_text("❗ الصيغة الصحيحة:\n/analyze GBPUSD M5")
        return

    result = analyze_market(symbol, tf)
    await update.message.reply_text(result)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
