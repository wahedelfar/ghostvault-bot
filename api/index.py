# api/index.py - النسخة الفخمة النهائية
import os, json, asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_NUMBER = "01063537686"
ADMIN_ID = 8530092344

PRODUCTS = {
    "max": {"name": "🎨 كورس 3D MAX الشامل", "price": 500, "desc": "1.77GB فيديوهات مسجلة - من الصفر للاحتراف - شامل الماتريال", "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file"},
    "voice": {"name": "🎙️ كورس التعليق الصوتي الاحترافي", "price": 500, "desc": "فويس أوفر - دوبلاج - تسجيل احترافي من البيت", "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file"},
    "makeup": {"name": "💄 كورس الميكاب برو", "price": 500, "desc": "ميكاب عرائس + سواريه - فيديوهات تطبيق عملي", "link": "https://www.mediafire.com/file/tqxe5181aveynly/file"},
    "canva": {"name": "🖌️ كورس كانفا + 5000 قالب", "price": 500, "desc": "قوالب برو جاهزة خاصة بينا - سوشيال - CV - بريزنتيشن", "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file"},
    "python": {"name": "🐍 كورس بايثون من الصفر", "price": 500, "desc": "فيديوهات مسجلة + مشاريع عملية + شهادة", "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file"},
    "kids": {"name": "👶 كورس برمجة للأطفال", "price": 500, "desc": "سكراتش وبايثون للأطفال - فيديوهات كرتونية ممتعة", "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file"},
    "excel": {"name": "📊 كورس الإكسيل المتقدم", "price": 500, "desc": "من المبتدئ للخبير - معادلات + داشبورد - فيديوهات", "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file"},
    "smartshop": {"name": "🛒 قالب SHOP X", "price": 500, "desc": "قالب متجر إلكتروني خاص بينا - كود نظيف - متجاوب", "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file"},
    "smartshop_v2": {"name": "🚀 قالب SHOP V2 المطور", "price": 1000, "desc": "إصدار مطور خاص بينا - دفع أونلاين - لوحة تحكم", "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file"},
    "atelier": {"name": "👗 قالب Atelier للملابس", "price": 1000, "desc": "قالب فخم خاص بينا لمتاجر الأزياء - تصميم راقي", "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file"},
}

def main_menu():
    kb = [[InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")] for k,p in PRODUCTS.items()]
    kb.append([InlineKeyboardButton("🔥 الباقة الكاملة 10 منتجات - 3000ج بدل 7000ج", callback_data="bundle")])
    return InlineKeyboardMarkup(kb)

WELCOME_TEXT = f"""
👻 **أهلاً بيك في Ghost Vault Egypt** 👻
المتجر رقم #1 للمنتجات الرقمية في مصر

━━━━━━━━━━━━━━━━━━━━
🎬 **كل الكورسات عبارة عن:**
✅ فيديوهات مسجلة بجودة عالية
✅ تحميل فوري بعد الدفع - مدى الحياة
✅ مشاهدة بدون نت بعد التحميل
✅ تحديثات مجانية للأبد

🛒 **القوالب:**
✅ أكواد خاصة بينا 100% - مش منتشرة
✅ تصميم عصري وسريع
✅ دعم فني لتثبيت القالب

━━━━━━━━━━━━━━━━━━━━
💳 **طريقة الدفع:**
فودافون كاش على: `{PAYMENT_NUMBER}`

⚠️ **مهم جداً لما تبعت السكرين:**
1- لازم السكرين يكون من تطبيق فودافون كاش
2- يبان فيه الرقم والمبلغ وتاريخ التحويل
3- **اكتب مع السكرين اسم المنتج اللي اشتريته**

مثال: تبعت الصورة وتكتب معاها:
`3D MAX` أو `الباقة` أو `كانفا`

━━━━━━━━━━━━━━━━━━━━
👇 **اختار المنتج اللي عايزه:**
"""

async def start_cmd(update, context):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu(), parse_mode='Markdown')

async def btn_handler(update, context):
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
                links = "\n\n".join([f"✅ {v['name']}:\n{v['link']}" for v in PRODUCTS.values()])
                msg = f"🎉 **مبروك! تم تأكيد دفع الباقة 3000ج**\n\n{links}\n\n💡 كل الروابط مدى الحياة\nشكراً لثقتك في Ghost Vault ❤️"
            else:
                p = PRODUCTS[prod_key]
                msg = f"🎉 **تم تأكيد دفع {p['price']}ج**\n\n📦 {p['name']}\n📝 {p['desc']}\n\n🔗 **رابط التحميل:**\n{p['link']}\n\n💡 الرابط مدى الحياة - حمله واحتفظ بيه\nشكراً لثقتك ❤️"
            await context.bot.send_message(chat_id=target_id, text=msg, parse_mode='Markdown')
            await q.edit_message_caption(caption=q.message.caption + f"\n\n✅ تم إرسال {PRODUCTS.get(prod_key, {'name':'الباقة'}).get('name','الباقة')}")
        except Exception as e:
            await q.answer(f"خطأ: {e}", show_alert=True)
        return

    if uid == ADMIN_ID and data.startswith("reject_"):
        target_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=target_id, text="❌ السكرين مرفوض - مش واضح أو المبلغ غلط\n\nابعت سكرين واضح من تطبيق فودافون كاش + اكتب اسم المنتج\nأو كلمنا: @waheed_elfar")
        await q.edit_message_caption(caption=q.message.caption + "\n\n❌ مرفوض")
        return

    if data.startswith("buy_"):
        k = data.replace("buy_","")
        p = PRODUCTS[k]
        txt = f"""
✅ **{p['name']}**

📝 {p['desc']}
💰 السعر: {p['price']} جنيه

━━━━━━━━━━━━
💳 **حول {p['price']}ج على:**
`{PAYMENT_NUMBER}`

📸 **بعد التحويل:**
ابعت سكرين شوت + اكتب معاه:
`{p['name']}`

عشان نعرف طلبك ونبعتلك الرابط بسرعة!
"""
        kb = [[InlineKeyboardButton(f"✅ حولت {p['price']}ج - هبعت السكرين", callback_data=f"paid_{k}")],[InlineKeyboardButton("⬅️ رجوع للقائمة", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data.startswith("paid_"):
        k = data.replace("paid_","")
        prod_name = PRODUCTS[k]['name'] if k in PRODUCTS else "الباقة"
        await q.edit_message_text(f"📸 **تمام! ابعت السكرين دلوقتي**\n\n⚠️ **مهم:** اكتب مع الصورة اسم المنتج:\n`{prod_name}`\n\nمثال: ابعت الصورة وفي الكابشن اكتب `{prod_name}`\n\nعشان نعرف طلبك بسرعة ونبعتلك الرابط!", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]))

    elif data=="bundle":
        txt = f"""
🔥 **الباقة الكاملة - 10 منتجات**

💰 **3000ج بدل 7000ج** (خصم 57%)

📦 هتاخد:
• 7 كورسات فيديو مسجلة
• 3 قوالب خاصة بينا

💳 **حول 3000ج على:**
`{PAYMENT_NUMBER}`

📸 بعدها ابعت السكرين + اكتب `الباقة`
"""
        kb = [[InlineKeyboardButton("✅ حولت 3000ج - هبعت السكرين", callback_data="paid_bundle")],[InlineKeyboardButton("⬅️ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data=="back":
        await q.edit_message_text(WELCOME_TEXT, reply_markup=main_menu(), parse_mode='Markdown')

async def photo_handler(update, context):
    user = update.message.from_user
    user_caption = update.message.caption or ""

    # نحاول نعرف المنتج من كلام العميل
    guessed_product = "غير محدد"
    lower_caption = user_caption.lower()
    for k,p in PRODUCTS.items():
        if k in lower_caption or p['name'].split()[1].lower() in lower_caption or str(p['price']) in lower_caption:
            guessed_product = p['name']
            break
    if "باقة" in lower_caption or "bundle" in lower_caption or "3000" in lower_caption:
        guessed_product = "الباقة الكاملة 3000ج"

    caption_text = f"""
🔔 **عميل جديد!**
━━━━━━━━━━━━
👤 {user.first_name} (@{user.username or 'بدون يوزر'})
🆔 `{user.id}`
📝 كاتب مع الصورة: "{user_caption or 'مكتبش حاجة'}"
🤖 تخمين المنتج: **{guessed_product}**

⚠️ اتأكد من السكرين: رقم {PAYMENT_NUMBER} والمبلغ
━━━━━━━━━━━━
👇 اختار هتبعتله أنهي رابط:
"""

    kb_rows = []
    for k,p in PRODUCTS.items():
        kb_rows.append([InlineKeyboardButton(f"✅ {p['name']} ({p['price']}ج)", callback_data=f"approve_{user.id}_{k}")])
    kb_rows.append([InlineKeyboardButton("✅🔥 الباقة الكاملة (3000ج)", callback_data=f"approve_{user.id}_bundle")])
    kb_rows.append([InlineKeyboardButton("❌ رفض - سكرين غلط", callback_data=f"reject_{user.id}")])

    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption_text, reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode='Markdown')
        await update.message.reply_text(f"✅ **تم استلام السكرين!**\n\n📦 المنتج: {user_caption or guessed_product}\n⏳ جاري المراجعة وهيوصلك الرابط خلال دقائق\n\n💡 كتبت اسم المنتج مع الصورة؟ لو لا ابعته تاني مع الاسم عشان نسرّع العملية", parse_mode='Markdown')
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

flask_app = Flask(__name__)

@flask_app.route('/', methods=['GET'])
def home():
    return "Bot is running! Ghost Vault Egypt - Fancy Version"

@flask_app.route('/api', methods=['POST', 'GET'])
@flask_app.route('/api/index', methods=['POST', 'GET'])
@flask_app.route('/', methods=['POST'])
def webhook():
    if request.method == 'GET':
        return "Bot is running! Ghost Vault"
    try:
        data = request.get_json(force=True)
        asyncio.run(process_update(data))
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return f"Error: {e}", 200

app = flask_app
