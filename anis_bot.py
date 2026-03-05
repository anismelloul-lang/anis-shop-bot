import telebot
from telebot import types
import os

# --- الإعدادات (جاهزة بمعلوماتك) ---
TOKEN = '8721101035:AAEZJC5s5OP_4usHvCMGryN9OA7t_mqHRh8'
ADMIN_ID = 1411512309  # المعرف الخاص بك الذي ظهر في الصورة
bot = telebot.TeleBot(TOKEN)
DB_FILE = "database.txt"

# دالة تحميل البيانات
def load_data():
    if not os.path.exists(DB_FILE):
        return {"ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "cash": 0.0, "daily_sales": 0.0}
    with open(DB_FILE, "r") as f:
        try:
            return eval(f.read())
        except:
            return {"ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "cash": 0.0, "daily_sales": 0.0}

# دالة حفظ البيانات وإرسال نسخة احتياطية
def save_data(data, backup=False):
    with open(DB_FILE, "w") as f:
        f.write(str(data))
    if backup:
        try:
            with open(DB_FILE, "rb") as doc:
                bot.send_document(ADMIN_ID, doc, caption="📦 تقرير الحسابات قبل التصفير")
        except:
            pass

# لوحة التحكم
def main_kb():
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add("📊 تقرير الميزانية", "🔄 تصفير مبيعات اليوم", "🔴 Ooredoo", "🔘 Djezzy", "🟢 Mobilis", "💰 الكاش (السيولة)")
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🏪 نظام محاسبة محل أنيس جاهز!", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == "🔄 تصفير مبيعات اليوم")
def reset(message):
    if message.from_user.id != ADMIN_ID: return
    data = load_data()
    # إرسال التقرير والنسخة قبل المسح
    save_data(data, backup=True)
    report = f"📜 تقرير المساء:\n📱 مبيعات اليوم: {data['daily_sales']} DA\n💵 سيولة الكاش: {data['cash']} DA"
    bot.send_message(ADMIN_ID, report)
    # تصفير اليومية
    data['daily_sales'] = 0.0
    data['cash'] = 0.0
    save_data(data)
    bot.reply_to(message, "✅ تم التصفير وإرسال النسخة الاحتياطية لخاص المدير.")

@bot.message_handler(func=lambda m: m.text in ["🔴 Ooredoo", "🔘 Djezzy", "🟢 Mobilis", "💰 الكاش (السيولة)"])
def add_amount(message):
    msg = bot.reply_to(message, f"أدخل المبلغ لـ {message.text}:")
    bot.register_next_step_handler(msg, process, message.text)

def process(message, cat):
    try:
        val = float(message.text)
        data = load_data()
        if "Ooredoo" in cat: data['ooredoo'] += val; data['daily_sales'] += val
        elif "Djezzy" in cat: data['djezzy'] += val; data['daily_sales'] += val
        elif "Mobilis" in cat: data['mobilis'] += val; data['daily_sales'] += val
        elif "الكاش" in cat: data['cash'] += val
        save_data(data)
        bot.send_message(message.chat.id, "✅ تم التسجيل.", reply_markup=main_kb())
    except:
        bot.reply_to(message, "❌ أرسل رقماً فقط!")

@bot.message_handler(func=lambda m: m.text == "📊 تقرير الميزانية")
def report_msg(message):
    data = load_data()
    text = f"📊 الميزانية الحالية:\n🔴 Ooredoo: {data['ooredoo']}\n🔘 Djezzy: {data['djezzy']}\n🟢 Mobilis: {data['mobilis']}\n💰 دخل كاش اليوم: {data['cash']}"
    bot.send_message(message.chat.id, text)

bot.polling(none_stop=True)
