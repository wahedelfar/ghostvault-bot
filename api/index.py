import os, json, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_NUMBER = "01063537686"

PRODUCTS = {
    "max": {"name": "🎨 3D MAX", "price": 500, "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file"},
    "voice": {"name": "🎙️ Voice Over", "price": 500, "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file"},
    "makeup": {"name": "💄 ميكاب", "price": 500, "link": "https://www.mediafire.com/file/tqxe5181aveynly/file"},
    "canva": {"name": "🖌️ كانفا", "price": 500, "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file"},
    "python": {"name": "🐍 بايثون", "price": 500, "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file"},
    "kids": {"name": "👶 أطفال", "price": 500, "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file"},
    "excel": {"name": "📊 أكسيل", "price": 500, "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file"},
    "smartshop": {"name": "🛒 SHOP X", "price": 500, "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file"},
    "smartshop_v2": {"name": "🚀 SHOP V2", "price": 1000, "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file"},
    "atelier": {"name": "👗 Atelier", "price": 1000, "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file"},
}

async def start(update, context):
    kb = []
    for k,p in PRODUCTS.items():
        kb.append([InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")])
    kb.append([InlineKeyboardButton("🔥 الباقة 3000ج", callback_data="bundle")])
    await update.message.reply_text(f"🛍️ متجر وحيد الفار\nفودافون كاش: {PAYMENT_NUMBER}", reply_markup=InlineKeyboardMarkup(kb))

async def btn(update, context):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("buy_"):
        k = q.data.replace("buy_","")
        context.user_data['prod']=k
        await q.edit_message_text(f"{PRODUCTS[k]['name']}\nحول {PRODUCTS[k]['price']}ج على {PAYMENT_NUMBER} وابعت سكرين", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ بعت الفلوس", callback_data="paid")]]))
    elif q.data=="paid" or q.data.startswith("paid_"):
        await q.edit_message_text("📸 ابعت سكرين شوت التحويل")
    elif q.data=="bundle":
        context.user_data['prod']="bundle"
        await q.edit_message_text(f"الباقة 3000ج\nحول على {PAYMENT_NUMBER} وابعت سكرين")

async def photo(update, context):
    k = context.user_data.get('prod','max')
    if k=="bundle":
        links = "\n".join([v['link'] for v in PRODUCTS.values()])
        await update.message.reply_text(f"✅ الباقة كاملة:\n{links}")
    else:
        await update.message.reply_text(f"✅ رابطك:\n{PRODUCTS[k]['link']}")

async def process(body):
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
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
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
