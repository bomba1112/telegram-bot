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

# --- KONFİQURASİYA ---
TOKEN = "8798520109:AAG0iV6LFwy7w-w3ot6_I80ETSzQoWrNKas"
# DİQQƏT: Bura öz OpenAI API Key-ini dırnaq daxilində yaz!
OPENAI_KEY = os.getenv("OPENAI_API_KEY") 

client = openai.OpenAI(api_key=OPENAI_KEY, http_client=httpx.Client(trust_env=False))
bot = Bot(token=TOKEN)
dp = Dispatcher()
WEB_APP_URL = "https://bomba1112.github.io/telegram-bot/" 

# --- FUNKSİYALAR ---

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception: pass
    return text

def create_pdf_report(data, ai_text):
    ai_text = ai_text.replace("**", "").replace("*", "")
    ai_text = re.sub(r'[-=_]{4,}', ' ', ai_text) 
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    f_r = "DejaVuSans.ttf"
    if not os.path.exists(f_r):
        urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans.ttf", f_r)
    pdf.add_font("DejaVu", "", f_r)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 10)
    pdf.multi_cell(0, 10, txt=ai_text)
    file_name = f"report_{datetime.now().strftime('%H%M%S')}.pdf"
    pdf.output(file_name)
    return file_name

# --- HANDLERS ---

@dp.message(Command("start"))
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚀 PANELİ AÇ", web_app=WebAppInfo(url=WEB_APP_URL))]], resize_keyboard=True)
    await message.answer("Xoş gəldin, Cəlil bəy. Hesabat üçün Paneli açın və ya şəkil/PDF atın:", reply_markup=markup)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    wait = await message.answer("📸 Şəkil analiz edilir...")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        
        # DÜZƏLİŞ: BytesIO pointerini düzgün idarə edirik
        img_buffer = io.BytesIO()
        await bot.download_file(file_info.file_path, destination=img_buffer)
        img_buffer.seek(0)
        base64_image = base64.b64encode(img_buffer.read()).decode('utf-8')

        prompt = "Sən profesional avto-diaqnostsan. Şəkildəki xəta kodlarını tap, Azərbaycan dilində izah et. Texniki detalların rusca qarşılığını mötərizədə yaz."
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer(f"Xəta: {str(e)}")
    finally:
        await wait.delete()

@dp.message(F.document)
async def handle_document(message: types.Message):
    if message.document.mime_type != 'application/pdf': return
    wait = await message.answer("📄 PDF analiz edilir...")
    file_info = await bot.get_file(message.document.file_id)
    f_name = message.document.file_name
    await bot.download_file(file_info.file_path, f_name)
    text = extract_text_from_pdf(f_name)[:15000]
    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Sənəd əsasında diaqnoz qoy: {text}"}])
    await message.answer(res.choices[0].message.content)
    os.remove(f_name)
    await wait.delete()

@dp.message(lambda m: m.web_app_data is not None)
async def handle_web_app_data(message: types.Message):
    res = json.loads(message.web_app_data.data)
    wait = await message.answer("🤖 Hesabat hazırlanır...")
    prompt = f"Avtomobil: {res['car_info']}, Xəta: {res['fault_code']}. Azərbaycan dilində rəsmi hesabat yaz. Texniki adları rusca mötərizədə qeyd et."
    ai = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user","content":prompt}])
    pdf = create_pdf_report(res, ai.choices[0].message.content)
    await bot.send_document(message.chat.id, FSInputFile(pdf))
    os.remove(pdf)
    await wait.delete()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
 
