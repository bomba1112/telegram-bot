import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai
import os

# Tokenləri birbaşa mənimsədin (və ya .env faylından istifadə edin)
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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" # Təhlükəsizlik üçün açarınızı kodda gizli saxlayın

# Dəyişən adının yuxarıdakı ilə eyni (OPENAI_API_KEY) olmasına diqqət edin
client = openai.OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salam! Avtomobil xətanızı yazın, kömək edim.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən professional avto-diaqnost mühəndisisən."},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer(f"Xəta baş verdi: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
