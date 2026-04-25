import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# 1. Giriş Məlumatları
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

# 2. Şəbəkə tənzimləməsi (Proxy xətası üçün)
http_client = httpx.Client(trust_env=False)

# 3. Bot və AI obyektləri
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client
)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# /start komandası
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Salam Jalil bəy! Professional Avto-Diaqnostika sisteminə xoş gəlmisiniz.\n\n"
        "Xəta kodunu daxil edin, mən sizə həm texniki səbəbi, həm də sadə həll yolunu təqdim edim."
    )

# Əsas məntiq hissəsi
@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Sən professional avto-diaqnost mühəndisisən. Cavablarını bu formatda qur:\n"
                        "1. Xətanın Texniki Adı (Azərbaycan və ingilis dilində).\n"
                        "2. Sadə İzah: Xətanın mahiyyətini bir ustanın başa düşəcəyi 'xalq dilində' izah et.\n"
                        "3. Texniki Səbəblər: Elektrik dövrəsi, sensor gərginliyi və ya mexaniki aşınma kimi mühəndis detallarını qısa qeyd et.\n"
                        "4. Həll Yolu: Addım-addım nəyi yoxlamalı (məsələn: multimetrlə yoxlama, təmizləmə və ya dəyişmə).\n"
                        "Üslubun həm professional, həm də anlaşıqlı olmalıdır."
                    )
                },
                {"role": "user", "content": message.text}
            ]
        )
        
        await message.answer(response.choices[0].message.content)

    except Exception as e:
        await message.answer(f"Sistem xətası: {str(e)}")

# Botu işə salma
async def main():
    print("Sistem aktivdir...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

