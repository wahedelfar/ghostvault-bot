# api/index.py - Ghost Vault Egypt - النسخة الفخمة + نظام الهدية الفيروسي (ضيف 5 وخد الدليل)
import os, json, asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
PAYMENT_NUMBER = "01063537686"
ADMIN_ID = 8530092344

GIFT_LINK_AR = "https://www.mediafire.com/file/j4zyoijzyvs0b94/Ghost-Vault-Free-Gift-AR.pdf/file"
CHANNEL_LINK = "https://t.me/Ghost_Vault_egy"
CHANNEL_USERNAME = "@Ghost_Vault_egy"
BOT_USERNAME = "ghostvault_egy_bot"

# ملاحظة: على Vercel الملف مؤقت، لكن للبداية كفاية. بعدين نحوله لـ KV أو Database
DATA_FILE = "/tmp/referrals.json"

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except:
        pass

PRODUCTS = {
    "max": {"name": "🎨 كورس 3D MAX الشامل", "price": 500, "desc": "1.77GB فيديوهات مسجلة - من الصفر للاحتراف - شامل الماتريال", "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file"},
    "voice": {"name": "🎙 كورس التعليق الصوتي الاحترافي", "price": 500, "desc": "فويس أوفر - دوبلاج - تسجيل احترافي من البيت", "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file"},
    "makeup": {"name": "💄 كورس الميكاب برو", "price": 500, "desc": "ميكاب عرائس + سواريه - فيديوهات تطبيق عملي", "link": "https://www.mediafire.com/file/tqxe5181aveynly/file"},
    "canva": {"name": "🖌 كورس كانفا + 5000 قالب", "price": 500, "desc": "قوالب برو جاهزة خاصة بينا - سوشيال - CV - بريزنتيشن", "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file"},
    "python": {"name": "🐍 كورس بايثون من الصفر", "price": 500, "desc": "فيديوهات مسجلة + مشاريع عملية + شهادة", "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file"},
    "kids": {"name": "👶 كورس برمجة للأطفال", "price": 500, "desc": "سكراتش وبايثون للأطفال - فيديوهات كرتونية ممتعة", "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file"},
    "excel": {"name": "📊 كورس الإكسيل المتقدم", "price": 500, "desc": "من المبتدئ للخبير - معادلات + داشبورد - فيديوهات", "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file"},
    "smartshop": {"name": "🛒 قالب SHOP X", "price": 500, "desc": "قالب متجر إلكتروني خاص بينا - كود نظيف - متجاوب", "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file"},
    "smartshop_v2": {"name": "🚀 قالب SHOP V2 المطور", "price": 1000, "desc": "إصدار مطور خاص بينا - دفع أونلاين - لوحة تحكم", "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file"},
    "atelier": {"name": "👗 قالب Atelier للملابس", "price": 1000, "desc": "قالب فخم خاص بينا لمتاجر الأزياء - تصميم راقي", "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file"},
}

def main_menu(user_id=None, invited=0):
    kb = []
    # زرار الهدية الفيروسية أول واحد
    kb.append([InlineKeyboardButton(f"🎁 هديتك المجانية - دليل Gumroad ({invited}/5)", callback_data="gift")])
    kb.append([InlineKeyboardButton(f"💰 رابط الإحالة الخاص بك - {invited}/5", callback_data="my_referral")])
    kb.extend([[InlineKeyboardButton(f"{p['name']} - {p['price']}ج", callback_data=f"buy_{k}")] for k,p in PRODUCTS.items()])
    kb.append([InlineKeyboardButton("🔥 الباقة الكاملة 10 منتجات - 3000ج بدل 7000ج", callback_data="bundle")])
    return InlineKeyboardMarkup(kb)

WELCOME_TEXT_TEMPLATE = """
👻 **أهلاً بيك في Ghost Vault Egypt** 👻
المتجر رقم #1 للمنتجات الرقمية في مصر

━━━━━━━━━━━━━━━━━━━━
🎁 **هديتك المجانية (قيمة 1000ج):**
دليل بيع المنتجات الرقمية على Gumroad
5 صفحات مصورة - خطة 7 أيام لأول مبيعة

📊 انت ضفت: {invited}/5 أعضاء
{status}

━━━━━━━━━━━━━━━━━━━━
🎬 **كل الكورسات عبارة عن:**
✅ فيديوهات مسجلة بجودة عالية
✅ تحميل فوري بعد الدفع - مدى الحياة
✅ تحديثات مجانية للأبد

🛒 ** قوالب المتاجر:**
✅ قوالب خاصة بينا 100% - مش منتشرة

━━━━━━━━━━━━━━━━━━━━
💳 **طريقة الدفع:**
فودافون كاش على: `{payment}`

👇 **اختار من القائمة:**
"""

async def start_cmd(update, context):
    args = context.args
    referrer = args[0] if args else None
    user_id = str(update.effective_user.id)
    data = load_data()

    # نظام الإحالة
    if referrer and referrer != user_id and referrer.isdigit():
        if user_id not in data:
            data[user_id] = {"invited": 0, "got_gift": False, "referrer": referrer}
        if referrer not in data:
            data[referrer] = {"invited": 1, "got_gift": False}
        else:
            # متزودش لو نفس الشخص دخل تاني
            # هنعد بس لو المستخدم جديد
            # للتبسيط: هنزود كل مرة start برابط احالة مختلف
            # في النسخة المتقدمة نعمل Set للمدعوين
            invited_list = data[referrer].get("invited_list", [])
            if user_id not in invited_list:
                invited_list.append(user_id)
                data[referrer]["invited"] = len(invited_list)
                data[referrer]["invited_list"] = invited_list
                try:
                    await context.bot.send_message(chat_id=int(referrer), text=f"🎉 حد جديد دخل من رابطك! بقى عندك {len(invited_list)}/5 دعوات. كمل 5 وخد الهدية!")
                except:
                    pass
        save_data(data)

    if user_id not in data:
        data[user_id] = {"invited": 0, "got_gift": False, "invited_list": []}
        save_data(data)

    invited = data.get(user_id, {}).get("invited", 0)
    got_gift = data.get(user_id, {}).get("got_gift", False)
    status = "✅ الهدية مفتوحة - دوس على الزرار وخدها!" if invited >=5 or got_gift else "🔒 ضيف 5 أعضاء للقناة وخدها فوراً"
    
    text = WELCOME_TEXT_TEMPLATE.format(invited=invited, status=status, payment=PAYMENT_NUMBER)
    await update.message.reply_text(text, reply_markup=main_menu(user_id, invited), parse_mode='Markdown')

async def btn_handler(update, context):
    q = update.callback_query
    await q.answer()
    data_str = q.data
    uid = q.from_user.id
    uid_str = str(uid)

    # أدمن - الموافقة
    if uid == ADMIN_ID and data_str.startswith("approve_"):
        _, target_id, prod_key = data_str.split("_", 2)
        target_id = int(target_id)
        try:
            if prod_key == "bundle":
                links = "\n\n".join([f"✅ {v['name']}:\n{v['link']}" for v in PRODUCTS.values()])
                msg = f"🎉 **مبروك! تم تأكيد دفع الباقة 3000ج**\n\n{links}\n\n💡 كل الروابط مدى الحياة\nشكراً لثقتك في Ghost Vault ❤"
            else:
                p = PRODUCTS[prod_key]
                msg = f"🎉 **تم تأكيد دفع {p['price']}ج**\n\n📦 {p['name']}\n📝 {p['desc']}\n\n🔗 **رابط التحميل:**\n{p['link']}\n\n💡 الرابط مدى الحياة\nشكراً لثقتك ❤"
            await context.bot.send_message(chat_id=target_id, text=msg, parse_mode='Markdown')
            await q.edit_message_caption(caption=q.message.caption + f"\n\n✅ تم إرسال {PRODUCTS.get(prod_key, {'name':'الباقة'}).get('name','الباقة')}")
        except Exception as e:
            await q.answer(f"خطأ: {e}", show_alert=True)
        return

    if uid == ADMIN_ID and data_str.startswith("reject_"):
        target_id = int(data_str.split("_")[1])
        await context.bot.send_message(chat_id=target_id, text="❌ السكرين مرفوض - مش واضح أو المبلغ غلط\n\nابعت سكرين واضح من تطبيق فودافون كاش + اكتب اسم المنتج\nأو كلمنا: @waheed_elfar")
        await q.edit_message_caption(caption=q.message.caption + "\n\n❌ مرفوض")
        return

    # تحميل البيانات
    db = load_data()
    invited = db.get(uid_str, {}).get("invited", 0)

    if data_str == "gift":
        if invited >= 5 or db.get(uid_str, {}).get("got_gift"):
            db[uid_str]["got_gift"] = True
            save_data(db)
            await q.message.reply_text(f"🎉 **مبروك! هديتك الفخمة جاهزة:**\n\n{GIFT_LINK_AR}\n\n📚 دليل 5 صفحات مصور\n- كيف تبيع على Gumroad\n- مصادر زيارات مجانية\n- خطة 7 أيام لأول مبيعة\n\n💡 الباقة الكاملة 10 منتجات بـ 3000ج بدل 7000ج - دوس /start", parse_mode='Markdown')
        else:
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 ادخل قناة Ghost Vault", url=CHANNEL_LINK)],
                [InlineKeyboardButton(f"🔄 حدث العداد ({invited}/5)", callback_data="gift")],
                [InlineKeyboardButton("💰 هات رابط الإحالة بتاعي", callback_data="my_referral")],
                [InlineKeyboardButton("⬅ رجوع للقائمة", callback_data="back")]
            ])
            await q.message.reply_text(f"🔒 **الهدية مقفولة!**\n\n📊 انت ضفت: {invited}/5 أعضاء\n\n**عشان تفتحها:**\n1. ادخل القناة {@Ghost_Vault_egy}\n2. ضيف 5 من صحابك (اعملهم Forward للقناة)\n3. خليهم يدوسوا على رابط الإحالة بتاعك\n4. ارجع دوس هنا\n\nشارك رابطك وهتاخدها أسرع!", reply_markup=markup, parse_mode='Markdown')

    elif data_str == "my_referral":
        referral_link = f"https://t.me/{BOT_USERNAME}?start={uid_str}"
        txt = f"💰 **رابطك الخاص للإحالة:**\n\n`{referral_link}`\n\nكل واحد يدخل من رابطك = 1 نقطة\n📊 عندك حاليا: {invited}/5\n\n🎁 5 نقاط = تاخد دليل Gumroad (1000ج)\n🔥 10 نقاط = تاخد كورس هدية\n💸 20 نقطة = 500ج فودافون كاش!\n\nشاركه في جروبات المصممين والربح من الانترنت!"
        kb = [[InlineKeyboardButton("🎁 شوف هدفي ({}/5)".format(invited), callback_data="gift")],[InlineKeyboardButton("⬅ رجوع", callback_data="back")]]
        await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str.startswith("buy_"):
        k = data_str.replace("buy_","")
        p = PRODUCTS[k]
        txt = f"✅ **{p['name']}**\n\n📝 {p['desc']}\n💰 السعر: {p['price']} جنيه\n\n━━━━━━━━━━━━\n💳 **حول {p['price']}ج على:**\n`{PAYMENT_NUMBER}`\n\n📸 **بعد التحويل:**\nابعت سكرين شوت + اكتب معاه:\n`{p['name']}`"
        kb = [[InlineKeyboardButton(f"✅ حولت {p['price']}ج - هبعت السكرين", callback_data=f"paid_{k}")],[InlineKeyboardButton("⬅ رجوع للقائمة", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str.startswith("paid_"):
        k = data_str.replace("paid_","")
        prod_name = PRODUCTS[k]['name'] if k in PRODUCTS else "الباقة"
        await q.edit_message_text(f"📸 **تمام! ابعت السكرين دلوقتي**\n\n⚠ **مهم:** اكتب مع الصورة اسم المنتج:\n`{prod_name}`\n\nمثال: ابعت الصورة وفي الكابشن اكتب `{prod_name}`", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ رجوع", callback_data="back")]]))

    elif data_str=="bundle":
        txt = f"🔥 **الباقة الكاملة - 10 منتجات**\n\n💰 **3000ج بدل 7000ج** (خصم 57%)\n\n📦 هتاخد:\n- 7 كورسات فيديو مسجلة\n- 3 قوالب خاصة بينا\n\n💳 **حول 3000ج على:**\n`{PAYMENT_NUMBER}`\n\n📸 بعدها ابعت السكرين + اكتب `الباقة`"
        kb = [[InlineKeyboardButton("✅ حولت 3000ج - هبعت السكرين", callback_data="paid_bundle")],[InlineKeyboardButton("⬅ رجوع", callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str=="back":
        db = load_data()
        invited = db.get(uid_str, {}).get("invited", 0)
        got_gift = db.get(uid_str, {}).get("got_gift", False)
        status = "✅ الهدية مفتوحة!" if invited >=5 or got_gift else f"🔒 ضيف 5 وخدها - عندك {invited}/5"
        text = WELCOME_TEXT_TEMPLATE.format(invited=invited, status=status, payment=PAYMENT_NUMBER)
        await q.edit_message_text(text, reply_markup=main_menu(uid_str, invited), parse_mode='Markdown')

async def photo_handler(update, context):
    user = update.message.from_user
    user_caption = update.message.caption or ""
    photo_file_id = None
    is_document = False
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
    elif update.message.document:
        photo_file_id = update.message.document.file_id
        is_document = True
    if not photo_file_id:
        return

    guessed_product = "غير محدد - العميل مبعتش اسم"
    txt = user_caption.lower()
    if any(x in txt for x in ["ميكاب", "makeup", "مكياج"]):
        guessed_product = "💄 كورس الميكاب برو"
    elif any(x in txt for x in ["ماكس", "max", "3d"]):
        guessed_product = "🎨 كورس 3D MAX"
    elif any(x in txt for x in ["كانفا", "canva", "قوالب"]):
        guessed_product = "🖌 كورس كانفا + 5000 قالب"
    elif any(x in txt for x in ["بايثون", "python"]):
        guessed_product = "🐍 كورس بايثون"
    elif any(x in txt for x in ["اطفال", "أطفال", "kids"]):
        guessed_product = "👶 كورس برمجة للأطفال"
    elif any(x in txt for x in ["اكسيل", "excel"]):
        guessed_product = "📊 كورس الإكسيل"
    elif "v2" in txt:
        guessed_product = "🚀 قالب SHOP V2"
    elif "shop" in txt or "متجر" in txt:
        guessed_product = "🛒 قالب SHOP X"
    elif "atelier" in txt or "ملابس" in txt:
        guessed_product = "👗 قالب Atelier"
    elif any(x in txt for x in ["باقة", "bundle", "3000"]):
        guessed_product = "🔥 الباقة الكاملة 3000ج"
    elif any(x in txt for x in ["فويس", "voice", "تعليق"]):
        guessed_product = "🎙 كورس التعليق الصوتي"

    caption_text = f"🔔 **عميل جديد!**\n━━━━━━━━━━━━\n👤 {user.first_name} (@{user.username or 'بدون يوزر'})\n🆔 `{user.id}`\n📝 كاتب: \"{user_caption or 'مكتبش حاجة'}\"\n🤖 المنتج: **{guessed_product}**\n📎 النوع: {'ملف' if is_document else 'صورة'}\n━━━━━━━━━━━━"
    kb_rows = []
    for k,p in PRODUCTS.items():
        kb_rows.append([InlineKeyboardButton(f"✅ {p['name']} ({p['price']}ج)", callback_data=f"approve_{user.id}_{k}")])
    kb_rows.append([InlineKeyboardButton("✅🔥 الباقة (3000ج)", callback_data=f"approve_{user.id}_bundle")])
    kb_rows.append([InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")])

    try:
        if is_document:
            await context.bot.send_document(chat_id=ADMIN_ID, document=photo_file_id, caption=caption_text, reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode='Markdown')
        else:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=caption_text, reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode='Markdown')
        await update.message.reply_text(f"✅ **تم استلام السكرين!**\n\n📦 المنتج: **{guessed_product}**\n⏳ جاري المراجعة وهيوصلك الرابط خلال دقائق", parse_mode='Markdown')
    except Exception as e:
        print(f"ADMIN ERROR {e}")

async def process_update(data):
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(btn_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, photo_handler))
    await app.initialize()
    await app.process_update(Update.de_json(data, app.bot))
    await app.shutdown()

flask_app = Flask(__name__)

@flask_app.route('/', methods=['GET'])
def home():
    return "Bot is running! Ghost Vault Egypt - Viral Gift"

@flask_app.route('/api', methods=['POST', 'GET'])
@flask_app.route('/api/index', methods=['POST', 'GET'])
@flask_app.route('/', methods=['POST'])
def webhook():
    if request.method == 'GET':
        return "Bot is running! Ghost Vault - Viral"
    try:
        data = request.get_json(force=True)
        asyncio.run(process_update(data))
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return f"Error: {e}", 200

app = flask_app
