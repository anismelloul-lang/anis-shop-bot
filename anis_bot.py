import telebot
from telebot import types
import os

# --- الإعدادات (بناءً على معلوماتك) ---
TOKEN = "8721101035:AAEZJC5s5OP_4usHvCMGryN9OA7t_mqHRh8"
ADMIN_ID = 1411512309 # ID أنيس ملوك
bot = telebot.TeleBot(TOKEN)
DB_FILE = "database.txt"

# دالة تحميل البيانات
def load_data():
    if not os.path.exists(DB_FILE):
        return {"ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "total_cash": 0.0, "daily_sales": 0.0, "daily_cash_added": 0.0}
    with open(DB_FILE, "r") as f:
        try:
            return eval(f.read())
        except:
            return {"ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "total_cash": 0.0, "daily_sales": 0.0, "daily_cash_added": 0.0}

# دالة حفظ البيانات
def save_data(data, send_backup=False):
    with open(DB_FILE, "w") as f:
        f.write(str(data))
    if send_backup:
        try:
            with open(DB_FILE, "rb") as doc:
                bot.send_document(ADMIN_ID, doc, caption="📦 نسخة احتياطية للحسابات قبل تصفير الميزان اليومي")
        except: pass

# لوحة التحكم
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = ["📊 ميزان اليوم", "🔄 تصفير الحساب اليومي", "🔴 رصيد Ooredoo", "🔘 رصيد Djezzy", "🟢 رصيد Mobilis", "💰 رصيد الكاش الكلي", "📥 إضافة كاش لليوم"]
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحباً أنيس! نظام ميزان المحل جاهز 🏪", reply_markup=main_keyboard())

# معالجة الأوامر
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    data = load_data()
    text = message.text

    if text == "📊 ميزان اليوم":
        # حساب الفرق: الكاش المدخل اليوم ناقص الرصيد المنقوص من الشبكات
        diff = data['daily_cash_added'] - data['daily_sales']
        status = "✅ الحساب مثالي (0)" if diff == 0 else f"⚠️ الفرق: {diff} DA"
        
        res = (f"🏦 حالة أرصدة المحل (ثابتة):\n"
               f"--------------------------\n"
               f"🔴 Ooredoo: {data['ooredoo']} DA\n"
               f"🔘 Djezzy: {data['djezzy']} DA\n"
               f"🟢 Mobilis: {data['mobilis']} DA\n"
               f"💰 رصيد الكاش الكلي: {data['total_cash']} DA\n"
               f"--------------------------\n"
               f"📈 حسابات ميزان اليوم:\n"
               f"📥 كاش دخل اليوم: {data['daily_cash_added']} DA\n"
               f"📱 رصيد خرج من الشبكات: {data['daily_sales']} DA\n"
               f"⚖️ {status}")
        bot.send_message(message.chat.id, res)

    elif text == "🔄 تصفير الحساب اليومي":
        # إرسال التقرير والنسخة الاحتياطية
        report = f"📜 تقرير ميزان المساء:\nرصيد خرج: {data['daily_sales']}\nكاش دخل: {data['daily_cash_added']}"
        bot.send_message(ADMIN_ID, report)
        save_data(data, send_backup=True)
        # تصفير الميزان اليومي فقط، مع بقاء أرصدة الشبكات والكاش ثابتة
        data['daily_sales'] = 0.0
        data['daily_cash_added'] = 0.0
        save_data(data)
        bot.reply_to(message, "✅ تم تصفير حسابات اليوم فقط. أرصدة التعبئة والكاش الكلي بقيت كما هي.")

    elif text in ["🔴 رصيد Ooredoo", "🔘 رصيد Djezzy", "🟢 رصيد Mobilis", "💰 رصيد الكاش الكلي", "📥 إضافة كاش لليوم"]:
        msg = bot.reply_to(message, f"أدخل القيمة لـ {text} (استخدم - للنقص و + للزيادة):")
        bot.register_next_step_handler(msg, process_value, text)

def process_value(message, category):
    try:
        val = float(message.text)
        data = load_data()
        if "Ooredoo" in category: 
            data['ooredoo'] += val
            if val < 0: data['daily_sales'] += abs(val) # إذا نقصت رصيد، يحسب كمبيعات اليوم
        elif "Djezzy" in category:
            data['djezzy'] += val
            if val < 0: data['daily_sales'] += abs(val)
        elif "Mobilis" in category:
            data['mobilis'] += val
            if val < 0: data['daily_sales'] += abs(val)
        elif "الكاش الكلي" in category:
            data['total_cash'] += val
        elif "إضافة كاش" in category:
            data['daily_cash_added'] += val
            data['total_cash'] += val
        
        save_data(data)
        bot.send_message(message.chat.id, "✅ تم تحديث الرصيد بنجاح.")
    except:
        bot.send_message(message.chat.id, "❌ خطأ! أدخل أرقاماً فقط.")

bot.polling(none_stop=True)
