import asyncio
import os
import httpx
import urllib.request
import json
import re
import io
import base64
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
from fpdf import FPDF
import openai
import PyPDF2

# --- BURANI DƏYİŞ ---
TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
OPENAI_KEY = "BURA_OPENAI_API_AÇARINI_YAPIŞDIR"  # <--- Açarı buraya yaz!

WEB_APP_URL = "https://bomba1112.github.io/telegram-bot/" 

client = openai.OpenAI(api_key=OPENAI_KEY, http_client=httpx.Client(trust_env=False))
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- PDF-DƏN MƏTN ÇIXARMA ---
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"PDF xətası: {e}")
    return text

# --- ŞƏKLİ BASE64-Ə ÇEVİRMƏ (Vision üçün) ---
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- PDF HESABAT YARATMA (Orijinal rəngli versiya) ---
def create_pdf_report(data, ai_text):
    ai_text = ai_text.replace("**", "").replace("*", "")
    ai_text = re.sub(r'[-=_]{4,}', ' ', ai_text) 
    ai_text = re.sub(r'([^\s]{40})', r'\1 ', ai_text) 
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    f_r, f_b = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
    if not os.path.exists(f_r):
        urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans.ttf", f_r)
    if not os.path.exists(f_b):
        urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans-Bold.ttf", f_b)
        
    pdf.add_font("DejaVu", "", f_r)
    pdf.add_font("DejaVu", "B", f_b)
    pdf.add_page()
    
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(0, 20, "AVTO-DİAQNOSTİKA HESABATI", ln=True, align='C')
    
    pdf.set_y(45)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 10, f"Müştəri: {data.get('customer_name', 'Qeyd olunmayıb')}", ln=True)
    pdf.cell(0, 10, f"Avtomobil: {data.get('car_info', 'Qeyd olunmayıb')}", ln=True)
    pdf.cell(0, 10, f"Xəta Kodu: {data.get('fault_code', 'Qeyd olunmayıb')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_text_color(0, 100, 200)
    pdf.cell(0, 10, "SÜNİ İNTELLEKT ANALİZİ VƏ HƏLL YOLU:", ln=True)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("DejaVu", "", 10)
    
    for line in ai_text.split('\n'):
        if "%" in line:
            pdf.set_text_color(200, 0, 0)
            pdf.multi_cell(0, 8, line)
            pdf.set_text_color(40, 40, 40)
        else:
            pdf.multi_cell(0, 8, line)
    
    f_name = f"report_{datetime.now().strftime('%H%M%S')}.pdf"
    pdf.output(f_name)
    return f_name

# --- HANDLERS ---

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = [[KeyboardButton(text="🚀 PANELİ AÇ", web_app=WebAppInfo(url=WEB_APP_URL))]]
    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Xoş gəldiniz! Məlumatları daxil edin və ya diaqnostika şəklini/PDF-i bura atın:", reply_markup=markup)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    wait = await message.answer("📸 Şəkil analiz edilir...")
    file_info = await bot.get_file(message.photo[-1].file_id)
    content = await bot.download_file(file_info.file_path)
    b64_img = encode_image(content.read())

    prompt = ("Sən professional avto-mexaniksən. Şəkildəki xəta kodlarını oxu. "
              "Onları Azərbaycan dilində izah et və həll yollarını yaz. "
              "Texniki detalların adını mötərizədə rusca yaz (məs: yanacaq nasosu (бензонасос)). "
              "Ulduz (*) və ya qalın mətndən istifadə etmə.")
    
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt},
                      {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}]}]
        )
        await message.answer(res.choices[0].message.content)
    except Exception as e:
        await message.answer(f"Xəta: {e}")
    finally:
        await wait.delete()

@dp.message(F.document)
async def handle_document(message: types.Message):
    if message.document.mime_type != 'application/pdf':
        return await message.answer("Zəhmət olmasa yalnız PDF göndərin.")
    
    wait = await message.answer("📄 PDF analiz edilir...")
    file_info = await bot.get_file(message.document.file_id)
    f_path = f"./{message.document.file_name}"
    await bot.download_file(file_info.file_path, f_path)

    text = extract_text_from_pdf(f_path)[:12000]
    prompt = (f"Bu sənədə əsasən avtomobilin nasazlığını analiz et:\n\n{text}\n\n"
              f"Analizi Azərbaycan dilində yaz, detalların rusca qarşılığını mötərizədə qeyd et.")

    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Sən avto-mühəndissən."}, {"role": "user", "content": prompt}]
        )
        await message.answer(f"📋 **Sənəd üzrə analiz:**\n\n{res.choices[0].message.content}")
    finally:
        if os.path.exists(f_path): os.remove(f_path)
        await wait.delete()

@dp.message(lambda m: m.web_app_data is not None)
async def handle_web_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    wait = await message.answer("🤖 Hesabat hazırlanır...")
    
    prompt = (f"Avtomobil: {data['car_info']}, Xəta: {data['fault_code']}. "
              "Hesabatı Azərbaycan dilində yaz. Nasazlıqları faizlə sırala. "
              "Texniki detalların adını mötərizədə mütləq rusca yaz (məsələn: krank mili (коленвал)). "
              "Faiz işarəsini rəqəmdən sonra yaz (75%). Ulduz (*), HTML və ya qalın mətndən istifadə etmə!")
    
    ai = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role":"system","content":"Sən professional diaqnostsan."}, {"role":"user","content":prompt}]
    )
    
    f_pdf = create_pdf_report(data, ai.choices[0].message.content)
    await bot.send_document(message.chat.id, FSInputFile(f_pdf), caption="✅ Hesabat hazırdır.")
    os.remove(f_pdf)
    await wait.delete()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
