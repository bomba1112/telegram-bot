import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# 1. Tokenləri birbaşa dırnaq içində mənimsədin
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

# 2. Proxy xətasının qarşısını almaq üçün (əgər serverdə problem yaranarsa)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

# 3. Obyektləri yaradın (Dəyişən adının eyni olmasına diqqət edin)
client = openai.OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salam! Avtomobil xətanızı yazın, professional diaqnost olaraq kömək edim.")

@dp.message()
async def handle_message(message: types.Message):
    # Boş mesaj gələrsə cavab verməsin
    if not message.text:
        return

    try:
        # OpenAI API-yə sorğu göndərilməsi
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən professional avto-diaqnost mühəndisisən. İstifadəçilərə avtomobil xətaları barədə dəqiq və texniki məlumat verirsən."},
                {"role": "user", "content": message.text}
            ]
        )
        
        # Cavabı Telegram-a göndər
        answer = response.choices[0].message.content
        await message.answer(answer)
        
    except Exception as e:
        # Hər hansı xəta baş verərsə istifadəçiyə bildir
        await message.answer(f"Xəta baş verdi: {e}")

async def main():
    print("Bot işə düşdü...")
    # Köhnə mesajları nəzərə almadan yeni mesajları dinləməyə başla
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot dayandırıldı.")
