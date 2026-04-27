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
    
    # 1. LOGO (Yuxarıda, iri ölçüdə)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 40, 10, 130) # Orta hissədə iri loqo
        pdf.ln(55)
    
    # 2. SERVİS MƏLUMATLARI
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 8, "AVTODIAGNOZAI SERVİS / AUTO-TECH SERVICE", ln=True, align='C')
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 6, "Mütəxəssis: Cəlil bəy", ln=True, align='C')
    pdf.cell(0, 6, "Tel: +994 (XX) XXX XX XX | Ünvan: Bakı ş., Azərbaycan, Sumqayıt s.", ln=True, align='C')
    pdf.ln(10)
    
    # 3. BAŞLIQ VƏ HESABAT NÖMRƏSİ
    report_no = datetime.now().strftime("%d%m%Y-%H%M")
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, f"SÜNİ İNTELLEKT AVTODİAQNOSTİKA HESABATI №: {report_no}", ln=True, align='C', fill=True)
    pdf.ln(5)
    
    # 4. MÜŞTƏRİ VƏ AVTOMOBİL CƏDVƏLİ
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 10, "MÜŞTƏRİ VƏ AVTOMOBİL MƏLUMATLARI", ln=True)
    pdf.set_font("DejaVu", "", 10)
    
    # Sol tərəf (Müştəri)
    pdf.cell(95, 8, f"Ad, Soyad: {data['client_name']}", border=1)
    pdf.cell(95, 8, f"Tarix: {datetime.now().strftime('%d.%m.%r')}", border=1, ln=True)
    
    # Avtomobil
    pdf.cell(95, 8, f"Marka / Model: {data['car_info']}", border=1)
    pdf.cell(95, 8, f"Xəta Kodu: {data['fault_code']}", border=1, ln=True)
    pdf.ln(10)
    
    # 5. AI ANALİZİ (USTA RƏYİ)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 10, "USTA RƏYİ VƏ TÖVSİYƏLƏR (SÜNİ İNTELLEKT ANALİZİ)", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 7, txt=ai_text, border=0)
    pdf.ln(10)
    
    # 6. MÖHÜR VƏ İMZALAR
    curr_y = pdf.get_y()
    if curr_y > 220: # Əgər səhifədə yer azdırsa, möhürü növbəti səhifəyə keçir
        pdf.add_page()
        curr_y = 20
        
    if os.path.exists("mohur.png"):
        pdf.image("mohur.png", 130, curr_y, 50) # Sağ tərəfə möhür
        
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(90, 10, "Müştəri imzası: ________________", ln=0)
    pdf.cell(90, 10, "Usta (Diaqnost): ________________", ln=1, align='R')
    pdf.ln(35)
    
    # 7. FOOTER (Xəbərdarlıq qeydi)
    pdf.set_font("DejaVu", "", 8)
    disclaimer = "Bu hesabat yalnız diaqnostika anında avtomobilin elektron sistemlərinin vəziyyətini əks etdirir və təmir məqsədi daşımır."
    pdf.multi_cell(0, 5, txt=disclaimer, align='C')
    
    name = f"report_{data['client_name'].replace(' ','_')}.pdf"
    pdf.output(name); return name

@dp.message(Command("start"))
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚀 PANELİ AÇ", web_app=WebAppInfo(url=WEB_APP_URL))]], resize_keyboard=True)
    await message.answer(f"Salam, {message.from_user.first_name}!\n\nProfessional Diaqnostika Sisteminə xoş gəldiniz. Hesabat hazırlamaq üçün Paneli açın:", reply_markup=markup)

@dp.message(lambda m: m.web_app_data is not None)
async def handle_data(message: types.Message):
    res = json.loads(message.web_app_data.data)
    wait = await message.answer("🧠 Süni İntellekt analiz edir və rəsmi hesabatı hazırlayır...")
    try:
        # AI üçün xüsusi təlimat: ehtimallar və faizlər ilə yazmaq
        prompt = (f"Sən professional avto-mühəndissən. Avtomobil: {res['car_info']}, Xəta: {res['fault_code']}. "
                  "Hesabatı Azərbaycan dilində yaz. Ən böyük ehtimal olunan nasazlıqdan başlayaraq aşağıya doğru sırala. "
                  "Hər nasazlıq üçün ehtimal faizini (məs: 70%) qeyd et və görüləcək işləri (fiziki pini ölçmək, detalları yoxlamaq) dəqiq yaz.")
        
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
