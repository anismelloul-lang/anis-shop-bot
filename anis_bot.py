import telebot
from telebot import types
import os

TOKEN = "8721101035:AAEZJC5s5OP_4usHvCMGryN9OA7t_mqHRh8"
ADMIN_ID = 1411512309
bot = telebot.TeleBot(TOKEN)
DB_FILE = "database.txt"

def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "cash": 0.0,
            "daily_o_sold": 0.0, "daily_d_sold": 0.0, "daily_m_sold": 0.0, "daily_cash_in": 0.0
        }
    with open(DB_FILE, "r") as f:
        try: return eval(f.read())
        except: return load_data()

def save_data(data):
    with open(DB_FILE, "w") as f: f.write(str(data))

def generate_report(data):
    total_sold = data['daily_o_sold'] + data['daily_d_sold'] + data['daily_m_sold']
    diff = data['daily_cash_in'] - total_sold
    status = "✅ الحساب مثالي" if diff == 0 else f"⚠️ الفرق: {diff} DA"
    return (f"🏛️ وضعية المحل الحالية:\n"
            f"--------------------------\n"
            f"🔴 Ooredoo: {data['ooredoo']} DA\n"
            f"🔘 Djezzy: {data['djezzy']} DA\n"
            f"🟢 Mobilis: {data['mobilis']} DA\n"
            f"💵 الكاش الكلي: {data['cash']} DA\n"
            f"--------------------------\n"
            f"📈 حسابات ميزان اليوم:\n"
            f"📥 كاش مدخل: {data['daily_cash_in']} DA\n"
            f"📱 مبيعات شبكات: {total_sold} DA\n"
            f"⚖️ {status}")

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = ["📊 تقرير ميزان اليوم", "⚙️ تعديل الأرصدة يدوياً", "📥 إغلاق ميزانية المساء", "🔄 تصفير مبيعات اليوم"]
    markup.add(*(types.KeyboardButton(b) for b in btns))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🏪 نظام المحاسبة الذكي جاهز!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    data = load_data()
    if message.text == "📊 تقرير ميزان اليوم":
        bot.send_message(message.chat.id, generate_report(data))

    elif message.text == "⚙️ تعديل الأرصدة يدوياً":
        msg = bot.reply_to(message, "أدخل الزيادة أو النقصان (أوريدو جيزي موبيليس كاش):\nمثال: 5000 0 0 -1000")
        bot.register_next_step_handler(msg, manual_adjust)

    elif message.text == "📥 إغلاق ميزانية المساء":
        msg = bot.reply_to(message, "أدخل الأرصدة المتبقية الآن والكاش الموجود:\n(أوريدو جيزي موبيليس كاش)")
        bot.register_next_step_handler(msg, closing_budget)

    elif message.text == "🔄 تصفير مبيعات اليوم":
        data['daily_o_sold'] = data['daily_d_sold'] = data['daily_m_sold'] = data['daily_cash_in'] = 0.0
        save_data(data)
        bot.reply_to(message, "✅ تم تصفير ميزان اليوم بنجاح.")

def manual_adjust(message):
    try:
        vals = [float(x) for x in message.text.split()]
        data = load_data()
        data['ooredoo'] += vals[0]
        data['djezzy'] += vals[1]
        data['mobilis'] += vals[2]
        data['cash'] += vals[3]
        save_data(data)
        bot.send_message(message.chat.id, "✅ تم تحديث الخزنة.\n" + generate_report(data))
    except: bot.send_message(message.chat.id, "❌ خطأ في الإدخال.")

def closing_budget(message):
    try:
        vals = [float(x) for x in message.text.split()]
        data = load_data()
        data['daily_o_sold'] = data['ooredoo'] - vals[0]
        data['daily_d_sold'] = data['djezzy'] - vals[1]
        data['daily_m_sold'] = data['mobilis'] - vals[2]
        data['daily_cash_in'] = vals[3] - data['cash']
        data['ooredoo'], data['djezzy'], data['mobilis'], data['cash'] = vals
        save_data(data)
        bot.send_message(message.chat.id, "✅ تم الإغلاق بنجاح!\n" + generate_report(data))
    except: bot.send_message(message.chat.id, "❌ خطأ في الإدخال.")

bot.polling(none_stop=True)
        
