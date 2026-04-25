import asyncio
import os
import httpx  # Yeni əlavə edildi
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# 1. Tokenləri dırnaq içində birbaşa qeyd edin
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

# 2. Xətanın qarşısını almaq üçün proxy tənzimləmələrini ləğv edən xüsusi Client yaradırıq
# Bu hissə logda gördüyümüz SyncHttpxClientWrapper xətasını həll edir.
http_client = httpx.Client(trust_env=False)

# 3. Obyektləri yaradın
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client  # Sistemi aldatmadan birbaşa keçid veririk
)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salam Jalil bəy! Avtomobil diaqnostika botu aktivdir. Buyurun, xətanı yazın.")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən professional avto-diaqnost mühəndisisən. Texniki və dəqiq məlumat verirsən."},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer(f"Xəta baş verdi: {str(e)}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
