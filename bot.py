import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# 1. Məlumatlar (Dəqiq mənimsədilib)
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

# 2. Şəbəkə xətalarının (proxy/httpx) qarşısını almaq üçün təmiz Client yaradırıq
http_client = httpx.Client(trust_env=False)

# 3. Bot və OpenAI obyektlərini yaradırıq
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client
)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Start komandası üçün handler
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Salam Jalil bəy! Mən Süni İntellektli avto-diaqnost botuyam.\n\n"
        "Zəhmət olmasa avtomobilinizdəki xəta kodunu (məsələn: P0301) və ya "
        "nasazlıq barədə məlumatı yazın. Sizə Azərbaycan dilində kömək edəcəm."
    )

# Mesajları oxuyan və Azərbaycan dilində cavab verən əsas hissə
@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return

    try:
        # OpenAI-yə Azərbaycan dilində cavab verməsi üçün təlimat göndəririk
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Sən professional avto-diaqnost mühəndisisən. "
                        "Bütün cavabların, xəta təhlillərin və təmir tövsiyələrin "
                        "YALNIZ Azərbaycan dilində olmalıdır. "
                        "Texniki terminlərin (məsələn: 'misfire', 'throttle') "
                        "Azərbaycan dilində qarşılığını istifadə et, lazım gələrsə "
                        "mötərizədə ingiliscə adını qeyd et."
                    )
                },
                {"role": "user", "content": message.text}
            ]
        )
        
        # Süni intellektin cavabını bota göndəririk
        bot_answer = response.choices[0].message.content
        await message.answer(bot_answer)

    except Exception as e:
        # Hər hansı texniki xəta olarsa bura düşəcək
        await message.answer(f"Sistem xətası baş verdi: {str(e)}")

# Botu başladan funksiya
async def main():
    print("Bot hazırda aktivdir və mesajları gözləyir...")
    # Köhnə mesajları təmizləyib yeni sorğuları qəbul edirik
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot söndürüldü.")
