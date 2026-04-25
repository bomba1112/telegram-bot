import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# 1. Giriş Məlumatları
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

# 2. Şəbəkə tənzimləməsi
http_client = httpx.Client(trust_env=False)

# 3. Bot və AI obyektləri
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client
)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Salam Jalil bəy! Professional Avto-Diaqnostika sisteminə xoş gəlmisiniz.\n\n"
        "Xəta kodunu daxil edin, mən sizə usta dilində sadə və dəqiq izah verim."
    )

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
                        "Sən professional avto-diaqnost mühəndisisən. Cavablarını bu qaydalara uyğun yaz:\n"
                        "1. Terminologiya: 'Buji' yerinə 'Şam (sveça)', 'Bobin' yerinə 'Babin', 'Vana' yerinə 'Klapan', "
                        "'Piston' yerinə 'Porşen', 'Enjektör' yerinə 'Farsunka' sözlərini istifadə et.\n"
                        "2. Sadə İzah: Xətanı elə izah et ki, həm sürücü, həm də usta başa düşsün. 'Çəkiclə yoxla' kimi mənasız ifadələr işlətmə.\n"
                        "3. Struktur: \n"
                        "   - Xətanın adı\n"
                        "   - Nə baş verir? (Sadə dildə)\n"
                        "   - Səbəblər (Sveça, babin, farsunka və s.)\n"
                        "   - Nə etməli? (Yoxlama və təmir addımları)\n"
                        "4. Dil: Yalnız Azərbaycan dilində cavab ver."
                    )
                },
                {"role": "user", "content": message.text}
            ]
        )
        
        await message.answer(response.choices[0].message.content)

    except Exception as e:
        await message.answer(f"Sistem xətası: {str(e)}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
 
