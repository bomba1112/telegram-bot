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
    # AI mətndəki ulduzları təmizləyirik
    ai_text = ai_text.replace("**", "").replace("*", "")
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Şriftləri yükləyirik
    f_r, f_b = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
    if not os.path.exists(f_r): 
        urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans.ttf", f_r)
    if not os.path.exists(f_b): 
        urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.0/ttf/DejaVuSans-Bold.ttf", f_b)
    
    pdf.add_font("DejaVu", "", f_r)
    pdf.add_font("DejaVu", "B", f_b)
    
    pdf.add_page()
    
    # 1. LOGO 
    logo_file = "logo.png.jpg" if os.path.exists("logo.png.jpg") else "logo.png"
    if os.path.exists(logo_file):
        pdf.image(logo_file, 80, 10, 50) 
        pdf.set_y(60) 
    else:
        pdf.set_y(20)
    
    # 2. SERVİS VƏ MÜTƏXƏSSİS MƏLUMATLARI
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 8, "AVTODIAGNOZAI SERVİS", ln=True, align='C')
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 5, "Mütəxəssis: Cəlil bəy", ln=True, align='C')
    pdf.cell(0, 5, "Tel: +994 50 250 62 42 | Ünvan: Sumqayıt ş.", ln=True, align='C')
    pdf.ln(8)
    
    # 3. HESABAT BAŞLIĞI
    report_no = datetime.now().strftime("%d%m%Y-%H%M")
    pdf.set_font("DejaVu", "B", 11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, f"SÜNİ İNTELLEKT AVTODİAQNOSTİKA HESABATI №: {report_no}", ln=True, align='C', fill=True)
    pdf.ln(5)

    # 4. MÜŞTƏRİ VƏ AVTOMOBİL CƏDVƏLİ
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
    systems = [
        ("Mühərrik (ECU/PCM)", "ECU", "Mühərrik"),
        ("Sürətlər qutusu (TCM)", "TCM", "Sürətlər qutusu"),
        ("Əyləc (ABS/ESP)", "ABS", "Əyləc"),
        ("Təhlükəsizlik (SRS)", "SRS", "Hava yastığı")
    ]

    for sys_name, code_key, name_key in systems:
        is_error = name_key.lower() in ai_text.lower() or code_key.lower() in ai_text.lower()
        status = "Xəta var" if is_error else "Normal"
        code = data['fault_code'] if is_error else "-"
        desc = "Sistemdə nasazlıq aşkarlandı" if is_error else "Xəta yoxdur"
        
        pdf.cell(50, 8, sys_name, border=1)
        pdf.cell(25, 8, status, border=1, align='C')
        pdf.cell(30, 8, code, border=1, align='C')
        pdf.cell(85, 8, desc, border=1, ln=1)
    
    pdf.ln(8)

    # 6. AI ANALİZİ - SƏTİR SƏTİR RƏNGLƏMƏ
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 10, "USTA RƏYİ VƏ TÖVSİYƏLƏR (AI ANALİZİ)", ln=True)
    
    # Mətni sətirlərə bölürük
    for line in ai_text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3) # Boş sətirdə kiçik məsafə
            continue
            
        # ƏGƏR SƏTİRDƏ % İŞARƏSİ VARSA, QIRMIZI VƏ QALIN ET
        if "%" in line:
            pdf.set_text_color(220, 0, 0) # Qırmızı
            pdf.set_font("DejaVu", "B", 10) # Qalın
        else:
            pdf.set_text_color(0, 0, 0) # Qara
            pdf.set_font("DejaVu", "", 10) # Normal
            
        pdf.multi_cell(0, 7, txt=line)
        
    # Sonrakı mətnlərin (disclaimer) qırmızı olmaması üçün rəngi sıfırlayırıq
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # 7. MÖHÜR 
    y_pos = pdf.get_y()
    if y_pos > 240: pdf.add_page(); y_pos = 20
    
    mohur_file = "mohur.png.jpg" if os.path.exists("mohur.png.jpg") else "mohur.png"
    if os.path.exists(mohur_file):
        pdf.image(mohur_file, 10, y_pos, 45) 
        pdf.set_y(y_pos + 50)
        
    # 8. DISCLAIMER 
    pdf.set_font("DejaVu", "", 8)
    disclaimer = "Bu hesabat yalnız diaqnostika anında avtomobilin elektron sistemlərinin vəziyyətini əks etdirir və təmir məqsədi daşımır."
    pdf.multi_cell(0, 5, txt=disclaimer, align='C')
    
    file_name = f"report_{data['client_name'].replace(' ','_')}.pdf"
    pdf.output(file_name); return file_name

@dp.message(Command("start"))
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🚀 PANELİ AÇ", web_app=WebAppInfo(url=WEB_APP_URL))]], resize_keyboard=True)
    await message.answer("Sistemə xoş gəldiniz. Hesabat hazırlamaq üçün Paneli açın:", reply_markup=markup)

@dp.message(lambda m: m.web_app_data is not None)
async def handle_data(message: types.Message):
    res = json.loads(message.web_app_data.data)
    wait = await message.answer("🧠 Süni İntellekt analiz edir...")
    try:
        # AI-yə ancaq təmiz mətn verməsini tapşırırıq
        prompt = (f"Sən professional avto-mühəndissən. Avtomobil: {res['car_info']}, Xəta: {res['fault_code']}. "
                  "Hesabatı Azərbaycan dilində yaz. Nasazlıqları faizlə sırala. "
                  "MÜHÜM: Faiz işarəsini rəqəmdən dərhal sonra yaz (məs: 75%). Əsla əvvələ qoyma. "
                  "Mətndə heç bir ulduz (*), HTML və ya qalınlaşdırma işarəsindən istifadə etmə. "
                  "Sən sadəcə mətni yaz, mətnin rənglənməsini mənim sistemim edəcək. "
                  "Fiziki olaraq hansı pini və ya kabeli yoxlamaq lazımdırsa, dəqiq yaz.")
        
        ai = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role":"system","content":"Sən professional diaqnostsan."},{"role":"user","content":prompt}]
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
