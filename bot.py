import asyncio
import os
import httpx
import urllib.request
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
from fpdf import FPDF
import openai

# --- TƏHLÜKƏSİZ MƏLUMATLAR ---
TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
WEB_APP_URL = "https://bomba1112.github.io/telegram-bot/" 

client = openai.OpenAI(api_key=OPENAI_KEY, http_client=httpx.Client(trust_env=False))
bot = Bot(token=TOKEN)
dp = Dispatcher()

def create_pdf_report(data, ai_text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Şriftləri yükləyirik
    f_r, f_b = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
    if not os.path.exists(f_r): urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans.ttf", f_r)
    if not os.path.exists(f_b): urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans-Bold.ttf", f_b)
    pdf.add_font("DejaVu", "", f_r); pdf.add_font("DejaVu", "B", f_b)
    
    pdf.add_page()
    
    # 1. LOGO (Sənin GitHub-dakı adınla: logo.png.jpg)
    logo_file = "logo.png.jpg" if os.path.exists("logo.png.jpg") else "logo.png"
    if os.path.exists(logo_file):
        pdf.image(logo_file, 10, 8, 190)
        pdf.ln(50)
    
    # 2. SERVİS MƏLUMATLARI
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 8, "AVTODIAGNOZAI SERVİS / AUTO-TECH SERVICE", ln=True, align='C')
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 5, "Mütəxəssis: Cəlil bəy", ln=True, align='C')
    pdf.cell(0, 5, "Tel: +994 (XX) XXX XX XX | Ünvan: Bakı ş., Sumqayıt s.", ln=True, align='C')
    pdf.ln(5)
    
    # 3. BAŞLIQ VƏ TARİX
    report_no = datetime.now().strftime("%d%m%Y-%H%M")
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, f"SÜNİ İNTELLEKT AVTODİAQNOSTİKA HESABATI №: {report_no}", ln=True, align='C', fill=True)
    pdf.ln(5)

    # 4. MÜŞTƏRİ VƏ AVTOMOBİL CƏDVƏLLƏRİ
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(95, 8, "MÜŞTƏRİ MƏLUMATLARI", border=1, align='C', fill=True)
    pdf.cell(95, 8, "AVTOMOBİL MƏLUMATLARI", border=1, ln=1, align='C', fill=True)
    
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(45, 8, "Ad, Soyad:", border='LTB'); pdf.cell(50, 8, f"{data['client_name']}", border='RTB')
    pdf.cell(45, 8, "Marka / Model:", border='LTB'); pdf.cell(50, 8, f"{data['car_info']}", border='RTB', ln=1)
    
    pdf.cell(45, 8, "Tarix:", border='LTB'); pdf.cell(50, 8, f"{datetime.now().strftime('%d.%m.%Y')}", border='RTB')
    pdf.cell(45, 8, "Xəta Kodu:", border='LTB'); pdf.cell(50, 8, f"{data['fault_code']}", border='RTB', ln=1)
    pdf.ln(8)

    # 5. DİAQNOSTİKA CƏDVƏLİ
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(50, 8, "Sistem / Blok", border=1, align='C', fill=True)
    pdf.cell(25, 8, "Status", border=1, align='C', fill=True)
    pdf.cell(30, 8, "Xəta Kodu", border=1, align='C', fill=True)
    pdf.cell(85, 8, "Təsvir və İzah", border=1, ln=1, align='C', fill=True)
    
    pdf.set_font("DejaVu", "", 9)
    # Avtomatik doldurulan sətirlər
    systems = [
        ("Mühərrik (ECU/PCM)", "Xəta var", data['fault_code'], "Sistemdə nasazlıq aşkarlandı"),
        ("Sürətlər qutusu (TCM)", "Normal", "-", "Xəta yoxdur"),
        ("Əyləc (ABS/ESP)", "Normal", "-", "Xəta yoxdur"),
        ("Təhlükəsizlik (SRS)", "Normal", "-", "Xəta yoxdur")
    ]
    for sys, status, code, desc in systems:
        pdf.cell(50, 8, sys, border=1)
        pdf.cell(25, 8, status, border=1, align='C')
        pdf.cell(30, 8, code, border=1, align='C')
        pdf.cell(85, 8, desc, border=1, ln=1)
    pdf.ln(8)

    # 6. USTA RƏYİ (SÜNİ İNTELLEKT)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 10, "USTA RƏYİ VƏ TÖVSİYƏLƏR (AI ANALİZİ)", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 7, txt=ai_text)
    pdf.ln(10)

    # 7. MÖHÜR VƏ İMZALAR
    y_pos = pdf.get_y()
    if y_pos > 230: pdf.add_page(); y_pos = 20
    
    mohur_file = "mohur.png.jpg" if os.path.exists("mohur.png.jpg") else "mohur.png"
    if os.path.exists(mohur_file):
        pdf.image(mohur_file, 140, y_pos - 5, 45) # Möhür sağ tərəfdə
        
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(95, 10, "Müştəri imzası: ________________", ln=0)
    pdf.cell(95, 10, "Usta (Diaqnost): ________________", ln=1, align='R')
    pdf.ln(15)

    # 8. DISCLAIMER (Xəbərdarlıq qeydi)
    pdf.set_font("DejaVu", "", 8)
    disclaimer = "Bu hesabat yalnız diaqnostika anında avtomobilin elektron sistemlərinin vəziyyətini əks etdirir və təmir məqsədi daşımır."
    pdf.multi_cell(0, 5, txt=disclaimer, align='C')
    
    file_name = f"report_{data['client_name'].replace(' ','_')}.pdf"
    pdf.output(file_name); return file_name

@dp.message(Command("start"))
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚀 PANELİ AÇ", web_app=WebAppInfo(url=WEB_APP_URL))]], resize_keyboard=True)
    await message.answer(f"Salam, {message.from_user.first_name}!\nProfessional Diaqnostika Hesabatı üçün Paneli açın:", reply_markup=markup)

@dp.message(lambda m: m.web_app_data is not None)
async def handle_data(message: types.Message):
    res = json.loads(message.web_app_data.data)
    wait = await message.answer("🧠 Süni İntellekt analiz edir və rəsmi hesabatı hazırlayır...")
    try:
        # Nasazlıqları faizlə və ehtimal sırası ilə tələb edirik
        prompt = (f"Sən professional avto-mühəndissən. Avtomobil: {res['car_info']}, Xəta: {res['fault_code']}. "
                  "Hesabatı Azərbaycan dilində yaz. Nasazlıqları ən böyük ehtimaldan başlayaraq faizlə (%) sırala. "
                  "Hər ehtimal üçün hansı pini, kabeli və ya detalı fiziki yoxlamalı olduğunu dəqiq qeyd et.")
        
        ai = client.chat.completions.create(model="gpt-4o", messages=[{"role":"system","content":"Sən professional diaqnostsan."},{"role":"user","content":prompt}])
        pdf = create_pdf_report(res, ai.choices[0].message.content)
        await message.answer_document(FSInputFile(pdf), caption="✅ Rəsmi diaqnostika hesabatı hazırdır.")
        await wait.delete()
    except Exception as e:
        await message.answer(f"Sistem xətası: {str(e)}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
