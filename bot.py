import asyncio
import os
import httpx
import urllib.request
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fpdf import FPDF
import openai

# --- TƏNZİMLƏMƏLƏR ---
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

http_client = httpx.Client(trust_env=False)
client = openai.OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

class DiagForm(StatesGroup):
    client_name = State()
    car_info = State()
    fault_code = State()

# PDF Yaradan Funksiya
def create_pdf_report(data, ai_text):
    pdf = FPDF()
    font_regular, font_bold = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
    if not os.path.exists(font_regular):
        urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans.ttf", font_regular)
    if not os.path.exists(font_bold):
        urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans-Bold.ttf", font_bold)
    
    pdf.add_font("DejaVu", "", font_regular)
    pdf.add_font("DejaVu", "B", font_bold)
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 35)
    
    pdf.set_font("DejaVu", 'B', 16)
    pdf.ln(40)
    pdf.cell(0, 10, "RƏSMİ DİAQNOSTİKA HESABATI", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("DejaVu", 'B', 12)
    pdf.cell(0, 10, "MÜŞTƏRİ VƏ AVTOMOBİL:", ln=True)
    pdf.set_font("DejaVu", "", 11)
    pdf.cell(0, 8, f"Ad: {data['client_name']}", ln=True)
    pdf.cell(0, 8, f"Avtomobil: {data['car_info']}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("DejaVu", 'B', 12)
    pdf.cell(0, 10, "MÜHƏNDİS ANALİZİ:", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 8, txt=ai_text)
    
    file_name = f"report_{data['client_name'].replace(' ', '_')}.pdf"
    pdf.output(file_name)
    return file_name

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    # DİQQƏT: Buradakı URL-i öz Mini App linkinlə dəyişəcəksən
    web_app_url = "https://celil-diag-panel.vercel.app" 
    
    markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚀 DİAQNOSTİKA PANELİNİ AÇ", web_app=WebAppInfo(url=web_app_url))]],
        resize_keyboard=True
    )
    await message.answer("Sistemi idarə etmək üçün aşağıdakı düyməyə basın:", reply_markup=markup)

# Paneldən (Mini App) gələn məlumatları emal edən hissə
@dp.message(lambda message: message.web_app_data is not None)
async def handle_webapp_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    wait_msg = await message.answer("🧠 Paneldən məlumat alındı. AI analiz edir...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən professional avto-diaqnost mühəndisisən. Terminlər: 'Şam', 'Babin', 'Farsunka', 'Beyin'."},
                {"role": "user", "content": f"Avto: {data['car_info']}, Xəta: {data['fault_code']}"}
            ]
        )
        ai_res = response.choices[0].message.content
        pdf_file = create_pdf_report(data, ai_res)
        await message.answer_document(FSInputFile(pdf_file), caption="✅ Paneldən göndərilən məlumatlar əsasında PDF hazırlandı.")
        await wait_msg.delete()
    except Exception as e:
        await message.answer(f"Xəta: {str(e)}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
 
