# api/index.py - متوافق مع Vercel الجديد
import os, json, asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_NUMBER = "01063537686"
ADMIN_ID = 8530092344

PRODUCTS = {
    "max": {"name": "🎨 3D MAX", "price": 500, "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file"},
    "voice": {"name": "🎙️ فويس أوفر", "price": 500, "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file"},
    "makeup": {"name": "💄 ميكاب", "price": 500, "link": "https://www.mediafire.com/file/tqxe5181aveynly/file"},
    "canva": {"name": "🖌️ كانفا", "price": 500, "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file"},
    "python": {"name": "🐍 بايثون", "price": 500, "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file"},
    "kids": {"name": "👶 أطفال", "price": 500, "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file"},
    "excel": {"name": "📊 أكسيل", "price": 500, "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file"},
    "smartshop": {"name": "🛒 SHOP X", "price": 500, "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file"},
    "smartshop_v2": {"name": "🚀 SHOP V2", "price": 1000, "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file"},
    "atelier": {"name": "👗 Atelier", "price": 1000, "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file"},
}

def main_menu():
    kb = [[InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")] for k,p in PRODUCTS.items()]
    kb.append([InlineKeyboardButton("🔥 الباقة 3000ج", callback_data="bundle")])
    return InlineKeyboardMarkup(kb)

async def start_cmd(update, context):
    txt = f"👻 Ghost Vault Egypt\n📚 كورسات وقوالب - تحميل فوري\n💳 فودافون كاش: {PAYMENT_NUMBER}\n👇 اختار:"
    await update.message.reply_text(txt, reply_markup=main_menu())

async def btn_handler(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id

    if uid == ADMIN_ID and data.startswith("approve_"):
        _, target_id, prod_key = data.split("_", 2)
        target_id = int(target_id)
        try:
            if prod_key == "bundle":
                links = "\n\n".join([f"{v['name']}: {v['link']}" for v in PRODUCTS.values()])
                await context.bot.send_message(chat_id=target_id, text=f"✅ تم التأكيد - الباقة:\n\n{links}")
            else:
                p = PRODUCTS[prod_key]
                await context.bot.send_message(chat_id=target_id, text=f"✅ تم تأكيد {p['price']}ج\n🔗 {p['name']}:\n{p['link']}")
            await q.edit_message_caption(caption=q.message.caption + "\n\n✅ تم الإرسال")
        except Exception as e:
            await q.answer(f"خطأ: {e}", show_alert=True)
        return

    if uid == ADMIN_ID and data.startswith("reject_"):
        target_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=target_id, text="❌ السكرين مرفوض - ابعت سكرين أوضح")
        await q.edit_message_caption(caption=q.message.caption + "\n\n❌ مرفوض")
        return

    if data.startswith("buy_"):
        k = data.replace("buy_","")
        p = PRODUCTS[k]
        txt = f"✅ {p['name']} - {p['price']}ج\n💳 حول على: {PAYMENT_NUMBER}"
        kb = [[InlineKeyboardButton("✅ هبعت السكرين", callback_data=f"paid_{k}")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("paid_"):
        await q.edit_message_text("📸 ابعت سكرين التحويل دلوقتي", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]))
    elif data=="bundle":
        txt = f"🔥 الباقة 3000ج\n💳 حول على: {PAYMENT_NUMBER}"
        kb = [[InlineKeyboardButton("✅ هبعت سكرين الباقة", callback_data="paid_bundle")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    elif data=="back":
        await q.edit_message_text("🏠 القائمة:", reply_markup=main_menu())

async def photo_handler(update, context):
    user = update.message.from_user
    caption_text = f"🔔 عميل جديد!\n👤 {user.first_name} (@{user.username})\n🆔 {user.id}\n📸 سكرين وصل"
    kb_rows = []
    for k,p in PRODUCTS.items():
        kb_rows.append([InlineKeyboardButton(f"✅ {p['name']}", callback_data=f"approve_{user.id}_{k}")])
    kb_rows.append([InlineKeyboardButton("✅ الباقة كاملة", callback_data=f"approve_{user.id}_bundle")])
    kb_rows.append([InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")])
    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption_text, reply_markup=InlineKeyboardMarkup(kb_rows))
        await update.message.reply_text("✅ تم الاستلام وجاري المراجعة ⏳")
    except Exception as e:
        print(f"ADMIN ERROR {e}")

async def process_update(data):
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(btn_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    await app.initialize()
    await app.process_update(Update.de_json(data, app.bot))
    await app.shutdown()

# Flask app - ده اللي Vercel بيدور عليه!
flask_app = Flask(__name__)

@flask_app.route('/', methods=['GET'])
def home():
    return "Bot is running! Ghost Vault"

@flask_app.route('/api', methods=['POST', 'GET'])
@flask_app.route('/api/index', methods=['POST', 'GET'])
@flask_app.route('/', methods=['POST'])
def webhook():
    if request.method == 'GET':
        return "Bot is running!"
    try:
        data = request.get_json(force=True)
        asyncio.run(process_update(data))
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return f"Error: {e}", 200

# Vercel بيدور على متغير اسمه app
app = flask_app
