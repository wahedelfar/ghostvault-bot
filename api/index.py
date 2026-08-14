import os, json, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

PAYMENT_NUMBER = "01063537686"
PAYMENT_METHOD = "فودافون كاش"
TOKEN = os.getenv("BOT_TOKEN")

PRODUCTS = {
    "max": {"name": "🎨 كورس 3D MAX كامل", "price": 500, "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file", "desc": "كورس كامل"},
    "voice": {"name": "🎙️ كورس التعليق الصوتي", "price": 500, "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file", "desc": "Voice Over"},
    "makeup": {"name": "💄 كورس ميكاب", "price": 500, "link": "https://www.mediafire.com/file/tqxe5181aveynly/file", "desc": "ميكاب"},
    "canva": {"name": "🖌️ كورس كانفا", "price": 500, "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file", "desc": "كانفا برو"},
    "python": {"name": "🐍 كورس بايثون", "price": 500, "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file", "desc": "بايثون"},
    "kids": {"name": "👶 برمجة أطفال", "price": 500, "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file", "desc": "للأطفال"},
    "excel": {"name": "📊 أكسيل", "price": 500, "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file", "desc": "أكسيل"},
    "smartshop": {"name": "🛒 SMART SHOP X", "price": 500, "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file", "desc": "قالب متجر"},
    "smartshop_v2": {"name": "🚀 SMART SHOP V2", "price": 1000, "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file", "desc": "مطور"},
    "atelier": {"name": "👗 Atelier", "price": 1000, "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file", "desc": "ملابس"}
}

async def start(update, context):
    keyboard = []
    for k,p in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")])
    keyboard.append([InlineKeyboardButton("🔥 الباقة 3000ج", callback_data="bundle")])
    await update.message.reply_text(f"🛍️ متجر وحيد الفار\nالدفع: {PAYMENT_METHOD} {PAYMENT_NUMBER}", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update, context):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("buy_"):
        k = q.data.replace("buy_","")
        p = PRODUCTS[k]
        context.user_data['selected_product']=k
        await q.edit_message_text(f"{p['name']}\nالسعر {p['price']}ج\nحول على {PAYMENT_NUMBER} وابعت سكرين", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ بعت الفلوس", callback_data=f"paid_{k}")]]))
    elif q.data.startswith("paid_"):
        await q.edit_message_text("📸 ابعت سكرين شوت التحويل")
    elif q.data=="bundle":
        await q.edit_message_text(f"🔥 الباقة 10 منتجات 3000ج\nحول على {PAYMENT_NUMBER}")

async def photo_handler(update, context):
    k = context.user_data.get('selected_product','max')
    if k=="bundle":
        links = "\n".join([f"{v['name']}: {v['link']}" for v in PRODUCTS.values()])
        await update.message.reply_text(f"الباقة كاملة:\n{links}")
    else:
        await update.message.reply_text(f"رابطك:\n{PRODUCTS[k]['link']}")

async def main_handler(body):
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    await app.initialize()
    await app.process_update(Update.de_json(body, app.bot))
    await app.shutdown()

class handler:
    def __init__(self, *args, **kwargs): pass
