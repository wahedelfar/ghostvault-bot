import os, json, asyncio, pathlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from http.server import BaseHTTPRequestHandler

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_NUMBER = "01063537686"
ADMIN_ID = 8530092344
TMP_FILE = "/tmp/orders.json" # ملف مؤقت يحفظ آخر طلب

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

def save_order(uid, prod):
    try:
        data = {}
        if pathlib.Path(TMP_FILE).exists():
            data = json.loads(pathlib.Path(TMP_FILE).read_text())
        data[str(uid)] = prod
        pathlib.Path(TMP_FILE).write_text(json.dumps(data))
    except: pass

def get_order(uid):
    try:
        if pathlib.Path(TMP_FILE).exists():
            data = json.loads(pathlib.Path(TMP_FILE).read_text())
            return data.get(str(uid))
    except: pass
    return None

def main_menu():
    kb = [[InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")] for k,p in PRODUCTS.items()]
    kb.append([InlineKeyboardButton("🔥 الباقة 3000ج", callback_data="bundle")])
    return InlineKeyboardMarkup(kb)

async def start(update, context):
    await update.message.reply_text(f"👻 Ghost Vault\n💳 فودافون كاش: {PAYMENT_NUMBER}\n👇 اختار الكورس:", reply_markup=main_menu())

async def btn(update, context):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id

    if uid == ADMIN_ID and data.startswith("approve_"):
        _, tid, prod = data.split("_", 2)
        tid=int(tid)
        if prod=="bundle":
            links = "\n\n".join([f"{v['name']}: {v['link']}" for v in PRODUCTS.values()])
            await context.bot.send_message(chat_id=tid, text=f"✅ تم التأكيد - الباقة:\n\n{links}")
        else:
            p=PRODUCTS[prod]
            await context.bot.send_message(chat_id=tid, text=f"✅ تم تأكيد {p['price']}ج\n🔗 {p['name']}:\n{p['link']}")
        await q.edit_message_caption(caption=q.message.caption+"\n\n✅ تم الإرسال")
        return
    if uid == ADMIN_ID and data.startswith("reject_"):
        tid=int(data.split("_")[1])
        await context.bot.send_message(chat_id=tid, text="❌ مرفوض - ابعت سكرين أوضح")
        await q.edit_message_caption(caption=q.message.caption+"\n\n❌ مرفوض")
        return

    if data.startswith("buy_"):
        k=data.replace("buy_","")
        save_order(uid, k) # نحفظ طلبه
        p=PRODUCTS[k]
        txt=f"✅ اخترت: {p['name']}\n💰 {p['price']}ج\n💳 حول على {PAYMENT_NUMBER}\n\n📸 بعد التحويل ابعت سكرين التحويل + اكتب في الكابشن: {k}"
        kb=[[InlineKeyboardButton(f"✅ هبعت سكرين {p['name']}", callback_data=f"paid_{k}")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("paid_"):
        k=data.replace("paid_","")
        save_order(uid, k)
        await q.edit_message_text(f"📸 تمام، ابعت سكرين تحويل {k} دلوقتي\nممكن تكتب مع الصورة كلمة {k} عشان نعرف بسرعة", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]))
    elif data=="bundle":
        save_order(uid, "bundle")
        await q.edit_message_text(f"🔥 الباقة 3000ج\n💳 حول على {PAYMENT_NUMBER}\n📸 ابعت السكرين واكتب bundle", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ هبعت سكرين الباقة", callback_data="paid_bundle")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]))
    elif data=="back":
        await q.edit_message_text("🏠 القائمة:", reply_markup=main_menu())

async def photo_handler(update, context):
    user = update.message.from_user
    caption = (update.message.caption or "").lower()
    saved = get_order(user.id)

    # نحاول نعرف المنتج من الكابشن
    detected = saved
    for k in PRODUCTS.keys():
        if k in caption or PRODUCTS[k]['name'].lower() in caption:
            detected = k
            break
    if "bundle" in caption or "الباقة" in caption:
        detected = "bundle"

    if not detected:
        detected = saved or "unknown"

    prod_name = PRODUCTS[detected]['name'] if detected in PRODUCTS else "الباقة الكاملة" if detected=="bundle" else "غير معروف"
    price = PRODUCTS[detected]['price'] if detected in PRODUCTS else 3000 if detected=="bundle" else "?"

    admin_caption = f"🔔 عميل جديد!\n👤 {user.first_name} (@{user.username})\n🆔 {user.id}\n📦 طلب: {prod_name} ({detected})\n💰 {price}ج\n📝 كابشن العميل: {update.message.caption or 'مفيش'}\n\nاختار الصح:"

    # الزر المقترح فوق
    kb_rows = []
    if detected in PRODUCTS or detected=="bundle":
        kb_rows.append([InlineKeyboardButton(f"✅ تأكيد {prod_name} (مقترح)", callback_data=f"approve_{user.id}_{detected}")])
    # باقي الأزرار
    for k,p in PRODUCTS.items():
        if k!=detected:
            kb_rows.append([InlineKeyboardButton(f"بعت {p['name']}", callback_data=f"approve_{user.id}_{k}")])
    kb_rows.append([InlineKeyboardButton("بعت الباقة", callback_data=f"approve_{user.id}_bundle")])
    kb_rows.append([InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")])

    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=admin_caption, reply_markup=InlineKeyboardMarkup(kb_rows))
        await update.message.reply_text(f"✅ استلمنا سكرين {prod_name}\nجاري المراجعة ⏳")
    except Exception as e:
        print(f"ADMIN ERROR {e}")
        await update.message.reply_text("✅ تم الاستلام")

async def process(body):
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    await app.initialize()
    await app.process_update(Update.de_json(body, app.bot))
    await app.shutdown()

class handler
