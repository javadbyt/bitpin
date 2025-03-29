import requests
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import os

# تنظیمات از متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
BITPIN_API_TOKEN = os.getenv('BITPIN_API_TOKEN')

CRYPTO_LIST = {'BTC': 'بیتکوین', 'ETH': 'اتریوم', 'USDT': 'تتر'}

def get_prices():
    url = "https://api.bitpin.ir/api/v1/market/currencies/"
    headers = {"Authorization": f"Bearer {BITPIN_API_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        prices = []
        for currency in data['results']:
            symbol = currency['code']
            if symbol in CRYPTO_LIST:
                price = int(float(currency['price']))
                prices.append(f"{CRYPTO_LIST[symbol]}: {price:,} تومان")
        return "\n".join(prices) if prices else "خطا!"
    except Exception as e:
        return f"خطا: {str(e)}"

async def send_message():
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        message = get_prices()
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
    except TelegramError as e:
        print(f"خطا: {e}")

async def main():
    while True:
        await send_message()
        await asyncio.sleep(60)  # هر ۱ دقیقه

if __name__ == "__main__":
    asyncio.run(main())
