import os, json, asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_NUMBER = "01063537686"
ADMIN_ID = 8084142659 # حسابك انت

PRODUCTS = {
    "max": {"name": "🎨 كورس 3D MAX كامل", "price": 500, "desc": "1.77GB احترافي", "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file"},
    "voice": {"name": "🎙️ كورس التعليق الصوتي", "price": 500, "desc": "فويس أوفر احترافي", "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file"},
    "makeup": {"name": "💄 كورس ميكاب", "price": 500, "desc": "ميكاب بروفيشنال", "link": "https://www.mediafire.com/file/tqxe5181aveynly/file"},
    "canva": {"name": "🖌️ كورس كانفا", "price": 500, "desc": "كانفا + قوالب برو", "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file"},
    "python": {"name": "🐍 كورس بايثون", "price": 500, "desc": "من الصفر", "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file"},
    "kids": {"name": "👶 كورس أطفال", "price": 500, "desc": "سكراتش وبايثون", "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file"},
    "excel": {"name": "📊 كورس أكسيل", "price": 500, "desc": "من المبتدئ للخبير", "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file"},
    "smartshop": {"name": "🛒 SHOP X", "price": 500, "desc": "قالب متجر", "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file"},
    "smartshop_v2": {"name": "🚀 SHOP V2", "price": 1000, "desc": "قالب متطور", "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file"},
    "atelier": {"name": "👗 Atelier", "price": 1000, "desc": "قالب ملابس فخم", "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file"},
}

def main_menu():
    kb = [[InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")] for k,p in PRODUCTS.items()]
    kb.append([InlineKeyboardButton("🔥 الباقة الكاملة 3000ج (بدل 7000ج)", callback_data="bundle")])
    return InlineKeyboardMarkup(kb)

async def start(update, context):
    txt = f"""👻 أهلاً بيك في Ghost Vault Egypt

📚 متجر كورسات وقوالب رقمية - تحميل فوري بعد تأكيد الدفع

💎 10 منتجات احترافية
💳 الدفع: فودافون كاش
📱 الرقم: {PAYMENT_NUMBER}

👇 اختار المنتج:"""
    await update.message.reply_text(txt, reply_markup=main_menu())

async def btn(update, context):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    data = q.data

    # === أزرار الأدمن (انت) ===
    if user_id == ADMIN_ID and data.startswith("approve_"):
        # approve_123456_max
        parts = data.split("_")
        target_id = int(parts[1])
        prod_key = "_".join(parts[2:])
        try:
            if prod_key == "bundle":
                links = "\n".join([f"{v['name']}: {v['link']}" for v in PRODUCTS.values()])
                await context.bot.send_message(chat_id=target_id, text=f"✅ تم تأكيد الدفع 3000ج\n\n🎉 الباقة الكاملة:\n{links}")
            else:
                p = PRODUCTS[prod_key]
                await context.bot.send_message(chat_id=target_id, text=f"✅ تم تأكيد الدفع {p['price']}ج\n\n🔗 رابط {p['name']}:\n{p['link']}\n\nشكراً لثقتك! ❤️")
            await q.edit_message_caption(caption=q.message.caption + "\n\n✅ تم التأكيد وإرسال الرابط للعميل")
        except Exception as e:
            await q.edit_message_text(f"خطأ في الإرسال: {e}")
        return

    if user_id == ADMIN_ID and data.startswith("reject_"):
        target_id = int(data.split("_")[1])
        try:
            await context.bot.send_message(chat_id=target_id, text="❌ السكرين مش واضح أو التحويل مش صحيح\n\nمن فضلك ابعت سكرين أوضح من تطبيق فودافون كاش فيه المبلغ والرقم\nأو كلمنا: @waheed_elfar")
            await q.edit_message_caption(caption=q.message.caption + "\n\n❌ تم الرفض")
        except: pass
        return

    # === أزرار العميل ===
    if data.startswith("buy_"):
        k = data.replace("buy_","")
        p = PRODUCTS[k]
        context.user_data['prod']=k
        txt = f"✅ {p['name']}\n📝 {p['desc']}\n💰 {p['price']}ج\n\n💳 حول على فودافون كاش: {PAYMENT_NUMBER}\n⚠️ لازم السكرين يكون من تطبيق فودافون كاش"
        kb = [[InlineKeyboardButton("✅ بعت الفلوس", callback_data="paid")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

    elif data=="bundle":
        context.user_data['prod']="bundle"
        txt = f"🔥 الباقة الكاملة 10 منتجات - 3000ج بدل 7000ج\n\n💳 حول 3000ج على {PAYMENT_NUMBER}"
        kb = [[InlineKeyboardButton("✅ حولت 3000ج", callback_data="paid")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))

    elif data=="paid":
        await q.edit_message_text("📸 ابعت سكرين شوت تحويل فودافون كاش دلوقتي\n(لازم يبان فيه الرقم والمبلغ)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]))

    elif data=="back":
        await q.edit_message_text("🏠 القائمة الرئيسية:", reply_markup=main_menu())

async def photo_handler(update, context):
    if 'prod' not in context.user_data:
        await update.message.reply_text("⚠️ اختار المنتج الأول من /start", reply_markup=main_menu())
        return

    k = context.user_data.get('prod')
    user = update.message.from_user
    prod_name = "الباقة الكاملة" if k=="bundle" else PRODUCTS[k]['name']
    price = "3000" if k=="bundle" else PRODUCTS[k]['price']

    # رسالة للعميل
    await update.message.reply_text(f"✅ تم استلام السكرين\n\nجاري مراجعة تحويل {price}ج لكورس {prod_name}\nهيتم إرسال الرابط خلال دقائق بعد التأكيد ⏳")

    # رسالة ليك انت (الأدمن) مع الصورة
    caption = f"🔔 عميل جديد!\n\n👤 {user.first_name} (@{user.username})\n🆔 {user.id}\n📦 {prod_name}\n💰 {price}ج\n\n⬇️ السكرين تحت - دوس تأكيد؟"
    kb = [
        [InlineKeyboardButton("✅ تأكيد وإرسال الرابط", callback_data=f"approve_{user.id}_{k}")],
        [InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")]
    ]
    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        print(f"Admin send error: {e}")

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
            self.send_response(200); self.end_headers(); self.wfile.write(f"Error: {e}".encode())
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot is running!")
