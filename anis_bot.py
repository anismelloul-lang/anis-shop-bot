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
            "daily_sold": 0.0, "daily_cash": 0.0
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
    markup.add(types.KeyboardButton("🔄 تصفير الحساب اليومي"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🏪 نظام الميزان الختامي جاهز يا أنيس", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    data = load_data()
    text = message.text

    if text == "📊 ميزان اليوم 📊":
        diff = data['daily_cash'] - data['daily_sold']
        if diff == 0:
            status = "0 (✅ الحساب مثالي)"
        elif diff > 0:
            status = f"+{diff} (⚠️ زيادة في الكاش)"
        else:
            status = f"{diff} (❌ نقص في الكاش)"

        res = (f"🏛️ حالة أرصدة المحل (ثابتة):\n"
               f"--------------------------\n"
               f"🔴 Ooredoo: {data['ooredoo']} DA\n"
               f"⚪ Djezzy: {data['djezzy']} DA\n"
               f"🟢 Mobilis: {data['mobilis']} DA\n"
               f"💰 رصيد الكاش الكلي: {data['cash']} DA\n"
               f"--------------------------\n"
               f"📈 حسابات ميزان اليوم:\n"
               f"📥 كاش دخل اليوم: {data['daily_cash']} DA\n"
               f"📱 رصيد خرج من الشبكات: {data['daily_sold']} DA\n"
               f"⚖️ الميزان: {status}")
        bot.send_message(message.chat.id, res)

    elif "رصيد" in text:
        key = "ooredoo" if "Ooredoo" in text else "djezzy" if "Djezzy" in text else "mobilis" if "Mobilis" in text else "cash"
        label = "المتبقي في الشريحة" if key != "cash" else "الموجود في الدرج الآن"
        msg = bot.reply_to(message, f"أدخل {label} (أو أرسل +مبلغ لشحن الخزنة يدوياً):")
        bot.register_next_step_handler(msg, process_balance, key)

    elif text == "🔄 تصفير الحساب اليومي":
        # رسالة التأكيد التفصيلية
        reset_msg = (f"🔄 تم تصفير الحساب اليومي بنجاح:\n"
                     f"--------------------------\n"
                     f"✅ تم تصفير مبيعات اليوم: 0.0 DA\n"
                     f"✅ تم تصفير مدخول الكاش: 0.0 DA\n"
                     f"--------------------------\n"
                     f"📌 ملاحظة: أرصدة الخزنة الثابتة لم تتغير وهي جاهزة ليوم جديد.")
        
        data['daily_sold'] = 0.0
        data['daily_cash'] = 0.0
        save_data(data)
        bot.send_message(message.chat.id, reset_msg, reply_markup=main_keyboard())

def process_balance(message, key):
    data = load_data()
    try:
        val = message.text
        if val.startswith('+') or val.startswith('-'):
            data[key] += float(val)
            bot.send_message(message.chat.id, f"✅ تم تحديث الخزنة يدوياً.\nرصيد {key} الجديد: {data[key]} DA")
        else:
            current_val = float(val)
            if key == "cash":
                data['daily_cash'] += (current_val - data['cash'])
            else:
                data['daily_sold'] += (data[key] - current_val)
            
            data[key] = current_val
            bot.send_message(message.chat.id, "✅ تم التحديث وحساب ميزان اليوم.")
        save_data(data)
    except: bot.send_message(message.chat.id, "❌ خطأ في الإدخال.")

bot.polling(none_stop=True)
