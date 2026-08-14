import os, json, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_NUMBER = "01063537686"
PAYMENT_METHOD = "فودافون كاش"
ADMIN_USERNAME = "@waheed_elfar"

PRODUCTS = {
    "max": {"name": "🎨 كورس 3D MAX كامل", "price": 500, "desc": "كورس 1.77GB احترافي من الصفر للاحتراف - شامل الملفات", "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file"},
    "voice": {"name": "🎙️ كورس التعليق الصوتي", "price": 500, "desc": "احتراف الفويس أوفر وأسرار التعليق الصوتي", "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file"},
    "makeup": {"name": "💄 كورس ميكاب أرتيست", "price": 500, "desc": "كورس ميكاب بروفيشنال كامل + شهادة", "link": "https://www.mediafire.com/file/tqxe5181aveynly/file"},
    "canva": {"name": "🖌️ كورس كانفا برو", "price": 500, "desc": "كانفا + 1000 قالب برو جاهز", "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file"},
    "python": {"name": "🐍 كورس بايثون", "price": 500, "desc": "برمجة بايثون من الصفر + مشاريع", "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file"},
    "kids": {"name": "👶 كورس برمجة أطفال", "price": 500, "desc": "سكراتش وبايثون للأطفال", "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file"},
    "excel": {"name": "📊 كورس أكسيل احترافي", "price": 500, "desc": "أكسيل من المبتدئ للخبير", "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file"},
    "smartshop": {"name": "🛒 قالب SMART SHOP X", "price": 500, "desc": "قالب متجر إلكتروني جاهز", "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file"},
    "smartshop_v2": {"name": "🚀 قالب SMART SHOP V2 المطور", "price": 1000, "desc": "النسخة المطورة + مميزات إضافية", "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file"},
    "atelier": {"name": "👗 قالب Atelier - ملابس", "price": 1000, "desc": "قالب متجر ملابس فخم", "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file"},
}

def main_menu():
    kb = []
    for k,p in PRODUCTS.items():
        kb.append([InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")])
    kb.append([InlineKeyboardButton("🔥 الباقة الكاملة - 3000ج بدلاً من 7000ج", callback_data="bundle")])
    return InlineKeyboardMarkup(kb)

async def start(update, context):
    text = f"""
👻 أهلاً بيك في متجر Ghost Vault Egypt

📚 متجر كورسات وقوالب رقمية جاهزة للتحميل الفوري

💎 عندنا 10 منتجات احترافية:
• كورسات تعليمية (3D MAX - فويس أوفر - ميكاب - كانفا - بايثون - برمجة أطفال - أكسيل)
• قوالب متاجر إلكترونية جاهزة

💳 الدفع: {PAYMENT_METHOD}
📱 الرقم: {PAYMENT_NUMBER}

👇 اختار المنتج اللي عايزه من القائمة تحت:
"""
    await update.message.reply_text(text, reply_markup=main_menu())

async def btn(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data.startswith("buy_"):
        k = data.replace("buy_","")
        p = PRODUCTS.get(k)
        if not p: return
        context.user_data['prod']=k
        txt = f"""
✅ اخترت: {p['name']}

📝 الوصف: {p['desc']}
💰 السعر: {p['price']} جنيه

💳 حول الفلوس على:
{PAYMENT_METHOD}: {PAYMENT_NUMBER}

⚠️ بعد التحويل اضغط الزر تحت وبعدين ابعت سكرين شوت التحويل (لازم يكون سكرين من فودافون كاش مش أي صورة)
"""
        kb = [
            [InlineKeyboardButton("✅ بعت الفلوس - ابعت سكرين التحويل", callback_data="paid")],
            [InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="back")]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

    elif data=="paid":
        if 'prod' not in context.user_data:
            await q.edit_message_text("اختار المنتج الأول من /start", reply_markup=main_menu())
            return
        await q.edit_message_text("📸 تمام، دلوقتي ابعت سكرين شوت تحويل فودافون كاش (لازم يبان فيه الرقم والمبلغ)\n\n⚠️ لو بعت أي صورة تانية غير سكرين التحويل مش هيتم التسليم", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]))

    elif data=="bundle":
        context.user_data['prod']="bundle"
        txt = f"""
🔥 الباقة الكاملة - 10 منتجات بسعر 3000ج بدلاً من 7000ج

هتاخد كل ده:
• 7 كورسات + 3 قوالب متاجر

💳 حول 3000ج على:
{PAYMENT_METHOD}: {PAYMENT_NUMBER}

بعد التحويل دوس الزر تحت
"""
        kb = [
            [InlineKeyboardButton("✅ حولت 3000ج - ابعت السكرين", callback_data="paid")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="back")]
        ]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

    elif data=="back":
        await q.edit_message_text("🏠 القائمة الرئيسية - اختار المنتج:", reply_markup=main_menu())

async def photo(update, context):
    if 'prod' not in context.user_data:
        await update.message.reply_text("⚠️ اختار المنتج الأول من /start قبل ما تبعت السكرين", reply_markup=main_menu())
        return

    k = context.user_data.get('prod')

    # هنا المفروض مراجعة يدوية - مش هنبعت الرابط تلقائياً لأي صورة
    if k=="bundle":
        await update.message.reply_text(f"""
✅ تم استلام سكرين شوت الباقة

جاري مراجعة التحويل 3000ج...

لو التحويل صحيح هبعتلك كل الروابط خلال دقائق.

لو مستعجل كلمني: {ADMIN_USERNAME}

⏳ ملاحظة: التسليم التلقائي للتجربة (هيتم مراجعته يدوياً بعدين):
الروابط هتتبعت بعد التأكيد
""")
    else:
        p = PRODUCTS[k]
        await update.message.reply_text(f"""
✅ تم استلام سكرين شوت كورس: {p['name']}

جاري مراجعة تحويل {p['price']}ج على {PAYMENT_NUMBER}

لو التحويل صحيح هتستلم الرابط خلال دقائق.

لو مستعجل كلمني: {ADMIN_USERNAME}

---
⏳ للتجربة السريعة (سيتم إلغاء التسليم التلقائي لاحقاً):
🔗 رابطك: {p['link']}
""")

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
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(200); self.end_headers(); self.wfile.write(f"Error: {e}".encode())
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot is running - Ghost Vault Store")
