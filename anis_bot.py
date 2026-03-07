import telebot
from telebot import types
import os

TOKEN = "8721101035:AAEZJC5s5OP_4usHvCMGryN9OA7t_mqHRh8"
bot = telebot.TeleBot(TOKEN)
DB_FILE = "database.txt"

def load_data():
    if not os.path.exists(DB_FILE):
        return {
            "ooredoo": 0.0, "djezzy": 0.0, "mobilis": 0.0, "cash": 0.0, 
            "print_cash": 0.0, "debts": 0.0, "daily_sold": 0.0, "daily_cash": 0.0
        }
    with open(DB_FILE, "r") as f:
        try: return eval(f.read())
        except: return load_data()

def save_data(data):
    with open(DB_FILE, "w") as f: f.write(str(data))

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 ميزان اليوم 📊"))
    markup.add(types.KeyboardButton("🔴 رصيد Ooredoo"), types.KeyboardButton("⚪ رصيد Djezzy"))
    markup.add(types.KeyboardButton("🟢 رصيد Mobilis"), types.KeyboardButton("💰 رصيد الكاش الكلي"))
    markup.add(types.KeyboardButton("🖨️ درج الطباعة"), types.KeyboardButton("📒 دفتر الديون"))
    markup.add(types.KeyboardButton("🔄 تصفير الحساب اليومي"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🏪 تم إضافة خانة الديون المستقلة يا أنيس!", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    data = load_data()
    text = message.text

    if text == "📊 ميزان اليوم 📊":
        diff = data['daily_cash'] - data['daily_sold']
        status = "0 (✅ مثالي)" if diff == 0 else f"{diff} ({'⚠️ زيادة' if diff > 0 else '❌ نقص'})"
        
        res = (f"🏛️ حالة أرصدة المحل (ثابتة):\n"
               f"--------------------------\n"
               f"🔴 Ooredoo: {data['ooredoo']} DA\n"
               f"⚪ Djezzy: {data['djezzy']} DA\n"
               f"🟢 Mobilis: {data['mobilis']} DA\n"
               f"💰 الكاش الكلي: {data['cash']} DA\n"
               f"🖨️ رصيد الطباعة: {data['print_cash']} DA\n"
               f"📒 إجمالي الديون: {data['debts']} DA\n"
               f"--------------------------\n"
               f"📈 ميزان اليوم:\n"
               f"📥 كاش اليوم: {data['daily_cash']} DA\n"
               f"📱 مبيعات الشبكات: {data['daily_sold']} DA\n"
               f"⚖️ الميزان: {status}")
        bot.send_message(message.chat.id, res)

    elif text == "📒 دفتر الديون":
        msg = bot.reply_to(message, f"إجمالي الديون الحالي: {data['debts']} DA\nأدخل القيمة الجديدة أو استخدم + للزيادة و - للنقصان:")
        bot.register_next_step_handler(msg, update_debts_only)

    elif text == "🖨️ درج الطباعة":
        msg = bot.reply_to(message, f"رصيد الطباعة: {data['print_cash']} DA\nأدخل التعديل يدوياً (+ أو -):")
        bot.register_next_step_handler(msg, update_print_only)

    elif "رصيد" in text:
        key = "ooredoo" if "Ooredoo" in text else "djezzy" if "Djezzy" in text else "mobilis" if "Mobilis" in text else "cash"
        msg = bot.reply_to(message, f"تحديث {text}:\nأدخل المتبقي مساءً أو استخدم + للشحن اليدوي:")
        bot.register_next_step_handler(msg, process_balance, key)

    elif text == "🔄 تصفير الحساب اليومي":
        data['daily_sold'] = data['daily_cash'] = 0.0
        save_data(data)
        bot.send_message(message.chat.id, "🔄 تم تصفير الميزان. (الديون والطباعة لم تتغير).")

def update_debts_only(message):
    data = load_data()
    try:
        val = message.text
        if val.startswith('+') or val.startswith('-'): data['debts'] += float(val)
        else: data['debts'] = float(val)
        save_data(data)
        bot.send_message(message.chat.id, f"✅ تم تحديث دفتر الديون: {data['debts']} DA")
    except: bot.send_message(message.chat.id, "❌ خطأ.")

def update_print_only(message):
    data = load_data()
    try:
        val = message.text
        if val.startswith('+') or val.startswith('-'): data['print_cash'] += float(val)
        else: data['print_cash'] = float(val)
        save_data(data)
        bot.send_message(message.chat.id, "✅ تم تحديث رصيد الطباعة.")
    except: bot.send_message(message.chat.id, "❌ خطأ.")

def process_balance(message, key):
    data = load_data()
    try:
        val = message.text
        if val.startswith('+') or val.startswith('-'):
            data[key] += float(val)
        else:
            current_val = float(val)
            if key == "cash": data['daily_cash'] += (current_val - data['cash'])
            else: data['daily_sold'] += (data[key] - current_val)
            data[key] = current_val
        save_data(data)
        bot.send_message(message.chat.id, "✅ تم التحديث بنجاح.")
    except: bot.send_message(message.chat.id, "❌ خطأ.")

bot.polling(none_stop=True)
        
