import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import openai

# 1. Giriş Məlumatları
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

http_client = httpx.Client(trust_env=False)

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
        "Xəta kodunu daxil edin. Mən sizə 'skan et' kimi mənasız məsləhətlər yox, "
        "kapotun altında dəqiq nəyi və necə yoxlamalı olduğunuzu deyəcəm."
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
                        "Sən professional avto-diaqnost mühəndisisən. İstifadəçilərin (ustalar) artıq skan edib xətanı alıblar. "
                        "Buna görə də ASLA 'diaqnostika cihazı ilə yoxla' və ya 'skan et' kimi sözlər işlətmə. "
                        "Sənin vəzifən xətadan SONRAKI fiziki addımları deməkdir.\n\n"
                        "Qaydalar:\n"
                        "1. Terminologiya: 'Buji' -> 'Şam (sveça)', 'Bobin' -> 'Babin', 'Enjektör' -> 'Farsunka', "
                        "'Piston' -> 'Porşen', 'Vana' -> 'Klapan', 'PCM/ECU' -> 'Beyin'.\n"
                        "2. Üslub: Birbaşa işə keç. 'Canlı məlumatlarda (Live Data) gərginliyə bax', 'Ştekeri çıxar, pini ölç' kimi danış.\n"
                        "3. Struktur:\n"
                        "   - Xətanın adı\n"
                        "   - Maşındakı əlaməti (məs: motor əsir, qaz yemir)\n"
                        "   - Fiziki Yoxlama Addımları (Məs: 1. Babinlərin yerini dəyiş, 2. Farsunkanın tokunu ölç)\n"
                        "   - Mühəndis qeydi: Gərginlik (V) və ya müqavimət (Ohm) dəyərlərini qeyd et."
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
 
