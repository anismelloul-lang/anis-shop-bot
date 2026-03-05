import telebot
from telebot import types
import os

# توكن البوت الخاص بك
TOKEN = '8721101035:AAEZJC5s5OP_4usHvCMGryN9OA7t_mqHRh8'
bot = telebot.TeleBot(TOKEN)
DB_FILE = "database.txt"

# دالة تحميل البيانات
def load_data():
    if not os.path.exists(DB_FILE):
        return {"ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "cash_total": 0.0, "sales_today": 0.0, "cash_in_today": 0.0}
    with open(DB_FILE, "r") as f:
        data = {"ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "cash_total": 0.0, "sales_today": 0.0, "cash_in_today": 0.0}
        for line in f:
            try:
                key, val = line.strip().split(":")
                data[key] = float(val)
            except: continue
        return data

# دالة حفظ البيانات
def save_data(data):
    with open(DB_FILE, "w") as f:
        for key, val in data.items():
            f.write(f"{key}:{val}\n")

db = load_data()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🔴 Ooredoo', '🎧 Djezzy', '🟢 Mobilis', '💵 الكاش (السيولة)', '📊 تقرير الميزانية', '🔄 تصفير مبيعات اليوم')
    bot.send_message(message.chat.id, "🏪 نظام المحاسبة الدائم للمحل:\n\n- الكاش والشرائح مستمرة.\n- المبيعات اليومية تُصفر للمراقبة.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['🔴 Ooredoo', '🎧 Djezzy', '🟢 Mobilis', '💵 الكاش (السيولة)'])
def ask_amount(message):
    names = {'🔴 Ooredoo': 'ooredoo', '🎧 Djezzy': 'djezzy', '🟢 Mobilis': 'mobilis', '💵 الكاش (السيولة)': 'cash_total'}
    msg = bot.send_message(message.chat.id, f"أدخل المبلغ لـ {message.text}:")
    bot.register_next_step_handler(msg, lambda m: update(m, names[message.text]))

@bot.message_handler(func=lambda m: m.text == '📊 تقرير الميزانية')
def show_report(message):
    sales = db['sales_today']
    cash_in = db['cash_in_today']
    balance = cash_in - sales
    
    res = (f"📊 **وضعية الحساب الآن:**\n"
           f"━━━━━━━━━━━━\n"
           f"⚖️ **توازن مبيعات اليوم:**\n"
           f"📱 مبيعات الشبكات: `{sales}` DA\n"
           f"💰 دخل للكاش اليوم: `{cash_in}` DA\n"
           f"🏁 الفرق: `{balance}` DA\n"
           f"━━━━━━━━━━━━\n"
           f"💎 **الأرصدة الإجمالية (مستمرة):**\n"
           f"💵 إجمالي كاش المحل: `{db['cash_total']}` DA\n"
           f"🔴 Ooredoo: `{db['ooredoo']}`\n"
           f"🎧 Djezzy: `{db['djezzy']}`\n"
           f"🟢 Mobilis: `{db['mobilis']}`")
    bot.send_message(message.chat.id, res, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '🔄 تصفير مبيعات اليوم')
def reset_daily(message):
    db['sales_today'] = 0.0
    db['cash_in_today'] = 0.0
    save_data(db)
    bot.send_message(message.chat.id, "✅ تم تصفير عداد المبيعات اليومية بنجاح.")

def update(m, key):
    try:
        val = float(m.text.replace(' ', ''))
        # إذا خصمت من الشبكة (بيع لزبون)
        if key in ['ooredoo', 'djezzy', 'mobilis'] and val < 0:
            db['sales_today'] += abs(val)
        # إذا أضفت للكاش (استلام ثمن البيع)
        if key == 'cash_total' and val > 0:
            db['cash_in_today'] += val
        db[key] += val
        save_data(db)
        bot.send_message(m.chat.id, "✅ تم التسجيل بنجاح.")
    except:
        bot.send_message(m.chat.id, "❌ خطأ! أرسل أرقاماً فقط.")

# استخدام infinity_polling لضمان عدم الانقطاع
bot.infinity_polling(timeout=20, long_polling_timeout=10)
