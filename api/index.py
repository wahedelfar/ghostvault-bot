import os, json, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler

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

async def start(update, context):
    txt = f"""👻 Ghost Vault Egypt
📚 كورسات وقوالب - تحميل فوري
💳 فودافون كاش: {PAYMENT_NUMBER}
👇 اختار:"""
    await update.message.reply_text(txt, reply_markup=main_menu())

async def btn(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id

    # أدمن
    if uid == ADMIN_ID and data.startswith("approve_"):
        _, target_id, prod_key = data.split("_", 2)
        target_id = int(target_id)
        try:
            if prod_key == "bundle":
                links = "\n\n".join([f"{v['name']}: {v['link']}" for v in PRODUCTS.values()])
                await context.bot.send_message(chat_id=target_id, text=f"✅ تم التأكيد - الباقة الكاملة:\n\n{links}")
            else:
                p = PRODUCTS[prod_key]
                await context.bot.send_message(chat_id=target_id, text=f"✅ تم تأكيد {p['price']}ج\n🔗 {p['name']}:\n{p['link']}")
            await q.edit_message_caption(caption=q.message.caption + "\n\n✅ تم الإرسال")
        except Exception as e:
            await q.answer(f"خطأ: {e}", show_alert=True)
        return

    if uid == ADMIN_ID and data.startswith("reject_"):
        target_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=target_id, text="❌ السكرين مرفوض - ابعت سكرين واضح أو كلم @waheed_elfar")
        await q.edit_message_caption(caption=q.message.caption + "\n\n❌ مرفوض")
        return

    # عميل
    if data.startswith("buy_"):
        k = data.replace("buy_","")
        p = PRODUCTS[k]
        txt = f"✅ {p['name']} - {p['price']}ج\n💳 حول على: {PAYMENT_NUMBER}\nبعدها ابعت سكرين التحويل"
        kb = [[InlineKeyboardButton("✅ هبعت السكرين", callback_data=f"paid_{k}")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("paid_"):
        k = data.replace("paid_","")
        await q.edit_message_text(f"📸 ابعت سكرين تحويل {PRODUCTS.get(k, {'price':3000})['price'] if k!='bundle' else 3000}ج دلوقتي\nمهم: ابعت الصورة هنا", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]))

    elif data=="bundle":
        txt = f"🔥 الباقة 3000ج بدل 7000ج\n💳 حول على: {PAYMENT_NUMBER}"
        kb = [[InlineKeyboardButton("✅ هبعت سكرين الباقة", callback_data="paid_bundle")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

    elif data=="back":
        await q.edit_message_text("🏠 القائمة:", reply_markup=main_menu())

async def photo_handler(update, context):
    user = update.message.from_user
    # هنحاول نعرف المنتج من آخر رسالة، لو مش عارفين هنبعت للأدمن يختار
    caption_text = f"🔔 عميل جديد!\n👤 {user.first_name} (@{user.username})\n🆔 {user.id}\n\n📸 سكرين تحويل وصل"

    # أزرار للأدمن يختار يبعت أنهي كورس
    kb_rows = []
    for k,p in PRODUCTS.items():
        kb_rows.append([InlineKeyboardButton(f"✅ بعت {p['name']}", callback_data=f"approve_{user.id}_{k}")])
    kb_rows.append([InlineKeyboardButton("✅ بعت الباقة كاملة", callback_data=f"approve_{user.id}_bundle")])
    kb_rows.append([InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")])

    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption_text, reply_markup=InlineKeyboardMarkup(kb_rows))
        await update.message.reply_text("✅ تم استلام السكرين وجاري المراجعة ⏳\nهيوصلك الرابط خلال دقائق بعد تأكيد الأدمن")
    except Exception as e:
        await update.message.reply_text(f"خطأ: {e} - كلم الأدمن @waheed_elfar")
        print(f"ADMIN SEND ERROR: {e} - ADMIN_ID {ADMIN_ID}")

async def process(body):
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    await app.initialize()
    await app.process_update(Update.de_json(body, app.bot))
    await app.shutdown()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length',0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            asyncio.run(process(data))
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
        except Exception as e:
            print(f"ERROR: {e}")
            self.send_response(200); self.end_headers(); self.wfile.write(f"Error: {e}".encode())
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot is running!")
