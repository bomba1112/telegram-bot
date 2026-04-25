import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# 1. TOKENLƏRİ DÜZGÜN QEYD EDİN
# DİQQƏT: os.environ.get istifadə etməyin, çünki o, sistemdə bu açarları axtarır və tapmayanda boş qaytarır.
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

# 2. PROXY VƏ HTTTPX XƏTALARININ QARŞISINI ALMAQ ÜÇÜN
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# 3. OBYEKTLƏRİ YARADIN
# Burada base_url=base_url yazmaq olmaz, çünki proqram base_url-in nə olduğunu bilmir.
client = openai.OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salam! Mən Süni İntellektli avto-diaqnost botuyam. Avtomobilinizdəki nasazlığı yazın, kömək edim.")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return

    try:
        # OpenAI API sorğusu
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən professional avto-diaqnost mühəndisisən. İstifadəçinin yazdığı problemlərə əsasən avtomobil xətalarını analiz edirsən."},
                {"role": "user", "content": message.text}
            ]
        )
        
        await message.answer(response.choices[0].message.content)
        
    except Exception as e:
        # Əgər yenə xəta olarsa, xətanın tam mətnini bota göndərsin ki, görək nədir
        await message.answer(f"Sistem xətası: {str(e)}")

async def main():
    print("Bot başladıldı...")
    # Köhnə və yığılıb qalmış mesajları təmizləyirik
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot dayandırıldı.")
