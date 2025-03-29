import requests
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# تنظیمات
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
BITPIN_API_TOKEN = os.getenv('BITPIN_API_TOKEN')

CRYPTO_LIST = {'BTC': 'بیتکوین', 'ETH': 'اتریوم', 'USDT': 'تتر'}

def create_session():
    """ساخت Session با قابلیت تکرار خودکار"""
    session = requests.Session()
    retries = Retry(
        total=5,  # 5 بار تکرار
        backoff_factor=1,  # تاخیر بین تکرارها: 1, 2, 4, 8, 16 ثانیه
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_prices():
    """دریافت قیمت ها با مدیریت خطا"""
    url = "https://api.bitpin.ir/api/v1/market/currencies/"
    headers = {"Authorization": f"Bearer {BITPIN_API_TOKEN}"}
    session = create_session()
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        prices = []
        for currency in data.get('results', []):
            symbol = currency.get('code')
            if symbol in CRYPTO_LIST:
                price = int(float(currency.get('price', 0)))
                prices.append(f"{CRYPTO_LIST[symbol]}: {price:,} تومان")
        
        return "\n".join(prices) if prices else "داده ای یافت نشد!"
    
    except requests.exceptions.RequestException as e:
        return f"خطای اتصال: {type(e).__name__}"
    except Exception as e:
        return f"خطای ناشناخته: {str(e)}"

async def send_message():
    """ارسال پیام با جلوگیری از ارسال خطا به کانال"""
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        message = get_prices()
        
        # فقط اگر خطا نباشد ارسال کن
        if "خطا" not in message and "داده" not in message:
            await bot.send_message(chat_id=CHANNEL_ID, text=message)
        else:
            print(f"عدم ارسال پیام: {message}")
            
    except TelegramError as e:
        print(f"خطای تلگرام: {e}")

async def main():
    """حلقه اصلی با مدیریت استثناها"""
    while True:
        try:
            await send_message()
            await asyncio.sleep(60)  # هر 1 دقیقه
        except Exception as e:
            print(f"خطای سیستمی: {str(e)}")
            await asyncio.sleep(300)  # 5 دقیقه تاخیر پس از خطای شدید

if __name__ == "__main__":
    # فعال کردن لاگ پیشرفته
    import logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # اجرای برنامه
    asyncio.run(main())
