import asyncio
import os
import httpx
import urllib.request  # YENİ: Şrift yükləmək üçün
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fpdf import FPDF
import openai

# 1. Giriş Məlumatları
TELEGRAM_TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_API_KEY = "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"

http_client = httpx.Client(trust_env=False)
client = openai.OpenAI(api_key=OPENAI_API_KEY, http_client=http_client)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Məlumat toplama mərhələləri
class DiagForm(StatesGroup):
    client_name = State()
    car_info = State()
    fault_code = State()

# PDF Yaradan Funksiya (AZƏRBAYCAN DİLİ DƏSTƏYİ İLƏ)
def create_pdf_report(data, ai_text):
    pdf = FPDF()
    
    # 1. Unicode Şriftləri avtomatik yükləyirik
    font_regular = "DejaVuSans.ttf"
    font_bold = "DejaVuSans-Bold.ttf"
    
    if not os.path.exists(font_regular):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf", font_regular)
    if not os.path.exists(font_bold):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans-Bold.ttf", font_bold)
        
    # 2. Şriftləri PDF-ə əlavə edirik
    pdf.add_font("DejaVu", "", font_regular)
    pdf.add_font("DejaVu", "B", font_bold)
    
    pdf.add_page()
    
    # Loqo
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 35)
    
    # Artıq "Helvetica" yerinə "DejaVu" istifadə edirik
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
    
    # Faylın adında boşluqları sətiraltı xətlə əvəz edirik ki, error verməsin
    safe_name = data['client_name'].replace(" ", "_")
    file_name = f"report_{safe_name}.pdf"
    pdf.output(file_name)
    return file_name

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Salam!\nProfessional Diaqnostika Hesabatı hazırlamaq üçün əvvəlcə **Müştərinin Adını və Soyadını** yazın:"
    )
    await state.set_state(DiagForm.client_name)

@dp.message(DiagForm.client_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(client_name=message.text)
    await message.answer("İndi isə **Avtomobilin modelini və ilini** yazın (məs: Prius 30, 2012):")
    await state.set_state(DiagForm.car_info)

@dp.message(DiagForm.car_info)
async def get_car(message: types.Message, state: FSMContext):
    await state.update_data(car_info=message.text)
    await message.answer("Son olaraq, cihazın göstərdiyi **Xəta Kodunu** daxil edin:")
    await state.set_state(DiagForm.fault_code)

@dp.message(DiagForm.fault_code)
async def handle_fault(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    wait_msg = await message.answer("🧠 AI mühəndis hesabatı hazırlayır və PDF yaradır...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sən professional avto-diaqnost mühəndisisən. Terminlər: 'Şam', 'Babin', 'Farsunka', 'Beyin'. Birbaşa fiziki addımları yaz: Live Data-da nəyə baxmalı, hansı pini ölçməli. Struktur: Xətanın adı, Əlamət, Fiziki yoxlama, Müəndis qeydi (V/Ohm)."},
                {"role": "user", "content": f"Avto: {user_data['car_info']}, Xəta: {message.text}"}
            ]
        )
        ai_res = response.choices[0].message.content
        
        pdf_file = create_pdf_report(user_data, ai_res)
        await message.answer_document(FSInputFile(pdf_file), caption="✅ Hesabat hazırdır. Çap edib müştəriyə təqdim edə bilərsiniz.")
        
        await wait_msg.delete()
        await state.clear() 

    except Exception as e:
        await message.answer(f"Sistem xətası: {str(e)}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
 
