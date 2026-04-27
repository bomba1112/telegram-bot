import asyncio
import os
import httpx
import urllib.request
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
from fpdf import FPDF
import openai

# --- TƏHLÜKƏSİZ MƏLUMATLAR ---
TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
# Açar artıq burada deyil, Railway-in Variables hissəsindədir
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
WEB_APP_URL = "https://bomba1112.github.io/telegram-bot/" 

client = openai.OpenAI(api_key=OPENAI_KEY, http_client=httpx.Client(trust_env=False))
bot = Bot(token=TOKEN)
dp = Dispatcher()

def create_pdf_report(data, ai_text):
    pdf = FPDF()
    f_r, f_b = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
    if not os.path.exists(f_r): urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans.ttf", f_r)
    if not os.path.exists(f_b): urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans-Bold.ttf", f_b)
    pdf.add_font("DejaVu", "", f_r); pdf.add_font("DejaVu", "B", f_b)
    pdf.add_page()
    if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, 35)
    pdf.set_font("DejaVu", 'B', 16); pdf.ln(40); pdf.cell(0, 10, "RƏSMİ HESABAT", ln=True, align='C')
    pdf.set_font("DejaVu", "", 11); pdf.ln(10)
    pdf.cell(0, 10, f"Müştəri: {data['client_name']}", ln=True)
    pdf.cell(0, 10, f"Avtomobil: {data['car_info']}", ln=True); pdf.ln(5)
    pdf.multi_cell(0, 8, txt=ai_text)
    name = f"report_{data['client_name'].replace(' ','_')}.pdf"
    pdf.output(name); return name

@dp.message(Command("start"))
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚀 PANELİ AÇ", web_app=WebAppInfo(url=WEB_APP_URL))]], resize_keyboard=True)
    await message.answer("Sistemi idarə etmək üçün Paneli açın:", reply_markup=markup)

@dp.message(lambda m: m.web_app_data is not None)
async def handle_data(message: types.Message):
    res = json.loads(message.web_app_data.data)
    wait = await message.answer("🧠 AI Analiz edir və PDF hazırlayır...")
    try:
        ai = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role":"system","content":"Sən professional avto-diaqnost mühəndisisən."},
                {"role":"user","content":f"Avto: {res['car_info']}, Xəta: {res['fault_code']}"}
            ]
        )
        pdf = create_pdf_report(res, ai.choices[0].message.content)
        await message.answer_document(FSInputFile(pdf), caption="✅ Hesabat hazırdır.")
        await wait.delete()
    except Exception as e:
        await message.answer(f"Sistem xətası: {str(e)}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
