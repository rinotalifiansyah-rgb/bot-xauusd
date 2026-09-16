.import asyncio
import yfinance as yf
import pandas as pd
import pandas_ta_classic as ta
from telegram import Bot

TELEGRAM_TOKEN = "8904405128:AAFLaNw2z-kerDeyDf-GcOfTp_RWmLhCgXY"
TELEGRAM_CHAT_ID = "1810284939"

async def kirim_pesan(teks):
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=teks)
        print("Pesan terkirim ke Telegram!")
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

async def cek_sinyal():
    print("Mengambil data harga XAUUSD...")
    try:
        df = yf.download(tickers="GC=F", period="1d", interval="5m", progress=False)
        if len(df) == 0:
            print("Gagal ambil data.")
            return

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['sma_fast'] = ta.sma(df['Close'], length=2)
        df['sma_mid']  = ta.sma(df['Close'], length=8)
        df['sma_slow'] = ta.sma(df['Close'], length=88)
        df['rsi']      = ta.rsi(df['Close'], length=14)
        df['atr']      = ta.atr(df['High'], df['Low'], df['Close'], length=14)

        f = float(df['sma_fast'].iloc[-2])
        m = float(df['sma_mid'].iloc[-2])
        s = float(df['sma_slow'].iloc[-2])
        r = float(df['rsi'].iloc[-2])
        atr = float(df['atr'].iloc[-2])
        harga_sekarang = float(df['Close'].iloc[-1])

        bull = f > m and m > s
        bear = f < m and m < s

        if bull and r > 52:
            pesan = f"🟢 XAUUSD BUY SIGNAL\n\n💵 Entry: {harga_sekarang:.2f}\n🛑 SL: {harga_sekarang - atr*2:.2f}\n🎯 TP: {harga_sekarang + atr*3:.2f}\n📊 RSI: {r:.1f}"
            await kirim_pesan(pesan)
            print("Sinyal BUY dikirim!")
        elif bear and r < 48:
            pesan = f"🔴 XAUUSD SELL SIGNAL\n\n💵 Entry: {harga_sekarang:.2f}\n🛑 SL: {harga_sekarang + atr*2:.2f}\n🎯 TP: {harga_sekarang - atr*3:.2f}\n📊 RSI: {r:.1f}"
            await kirim_pesan(pesan)
            print("Sinyal SELL dikirim!")
        else:
            print(f"WAIT | RSI: {r:.1f} | F:{f:.2f} M:{m:.2f} S:{s:.2f}")
    except Exception as e:
        print(f"Error analisa: {e}")

async def main():
    print("Bot XAUUSD 24 Jam dimulai...")
    await kirim_pesan("🤖 Bot Sinyal XAUUSD Aktif 24 Jam!\nSiap memantau pasar.")
    
    while True:
        await cek_sinyal()
        print("Menunggu 5 menit untuk cek berikutnya...")
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())
