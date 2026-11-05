# api/index.py - Global Courses (formerly Ghost Vault Egypt) - النسخة الفخمة + نظام الهدية الفيروسي (ضيف 5 وخد الدليل)
# v2 (2026-11-05): واجهة ثنائية اللغة (عربي/إنجليزي) + أزرار دفع PayPal للمنتجات
# اللي صاحب المتجر عامل لها صفحات دفع جاهزة بتحويل تلقائي للتحميل بعد الدفع.
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
    "max": {"name": "🎨 كورس 3D MAX الشامل", "name_en": "🎨 3D MAX Complete Course", "price": 500, "desc": "1.77GB فيديوهات مسجلة - من الصفر للاحتراف - شامل الماتريال", "desc_en": "1.77GB recorded videos - zero to pro, materials included", "link": "https://www.mediafire.com/file/bqh9zcbd5b9aas6/file", "paypal": "https://www.paypal.com/ncp/payment/PY4NQM59LSQ6A"},
    "voice": {"name": "🎙 كورس التعليق الصوتي الاحترافي", "name_en": "🎙 Professional Voice-Over Course", "price": 500, "desc": "فويس أوفر - دوبلاج - تسجيل احترافي من البيت", "desc_en": "Voice-over, dubbing & pro recording from home", "link": "https://www.mediafire.com/file/8xd42rfi8kqcg5o/file", "paypal": "https://www.paypal.com/ncp/payment/2E8FRGZVH5TNN"},
    "makeup": {"name": "💄 كورس الميكاب برو", "name_en": "💄 Makeup Pro Course", "price": 500, "desc": "ميكاب عرائس + سواريه - فيديوهات تطبيق عملي", "desc_en": "Bridal & soiree makeup - practical video lessons", "link": "https://www.mediafire.com/file/tqxe5181aveynly/file", "paypal": "https://www.paypal.com/ncp/payment/ELSNRTDWH3LBL"},
    "canva": {"name": "🖌 كورس كانفا + 5000 قالب", "name_en": "🖌 Canva Course + 5000 Templates", "price": 500, "desc": "قوالب برو جاهزة خاصة بينا - سوشيال - CV - بريزنتيشن", "desc_en": "Exclusive pro templates - social, CVs, presentations", "link": "https://www.mediafire.com/file/91uhbbhsspeak47/file", "paypal": "https://www.paypal.com/ncp/payment/JT72PBMUJ553C"},
    "python": {"name": "🐍 كورس بايثون من الصفر", "name_en": "🐍 Python From Zero Course", "price": 500, "desc": "فيديوهات مسجلة + مشاريع عملية + شهادة", "desc_en": "Recorded videos + practical projects + certificate", "link": "https://www.mediafire.com/file/87gtnmb7aj88a3m/file", "paypal": "https://www.paypal.com/ncp/payment/M728ATAB3ZT6N"},
    "kids": {"name": "👶 كورس برمجة للأطفال", "name_en": "👶 Kids Programming Course", "price": 500, "desc": "سكراتش وبايثون للأطفال - فيديوهات كرتونية ممتعة", "desc_en": "Scratch & Python for kids - fun cartoon videos", "link": "https://www.mediafire.com/file/j153m2pujkjcjoy/file", "paypal": "https://www.paypal.com/ncp/payment/H4QMV7FTXWMVN"},
    "excel": {"name": "📊 كورس الإكسيل المتقدم", "name_en": "📊 Advanced Excel Course", "price": 500, "desc": "من المبتدئ للخبير - معادلات + داشبورد - فيديوهات", "desc_en": "Beginner to expert - formulas + dashboards, in videos", "link": "https://www.mediafire.com/file/zzlkpmjxcslbq41/file", "paypal": "https://www.paypal.com/ncp/payment/BQFMFZQXP9XZ4"},
    "smartshop": {"name": "🛒 قالب SHOP X", "name_en": "🛒 SHOP X Store Template", "price": 500, "desc": "قالب متجر إلكتروني خاص بينا - كود نظيف - متجاوب", "desc_en": "Exclusive store template - clean code, fully responsive", "link": "https://www.mediafire.com/file/oiaf5fp9xnn5ku3/file"},
    "smartshop_v2": {"name": "🚀 قالب SHOP V2 المطور", "name_en": "🚀 SHOP V2 Advanced Template", "price": 1000, "desc": "إصدار مطور خاص بينا - دفع أونلاين - لوحة تحكم", "desc_en": "Advanced exclusive edition - online payment, dashboard", "link": "https://www.mediafire.com/file/oc1ao2lro2htc2v/file"},
    "atelier": {"name": "👗 قالب Atelier للملابس", "name_en": "👗 Atelier Fashion Template", "price": 1000, "desc": "قالب فخم خاص بينا لمتاجر الأزياء - تصميم راقي", "desc_en": "Luxury exclusive template for fashion stores", "link": "https://www.mediafire.com/file/iwjkg301jxb2lek/file"},
}

def pname(p, lang):
    return p["name_en"] if lang == "en" and p.get("name_en") else p["name"]

def pdesc(p, lang):
    return p["desc_en"] if lang == "en" and p.get("desc_en") else p["desc"]

def get_lang(db, uid_str):
    lang = db.get(uid_str, {}).get("lang")
    return lang if lang in ("ar", "en") else "ar"

LANG_CHOOSER_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton("🇪🇬 العربية", callback_data="lang_ar")],
    [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
])

TEXTS = {
    "ar": {
        "gift_btn": "🎁 هديتك المجانية - دليل Gumroad ({invited}/5)",
        "ref_btn": "💰 رابط الإحالة الخاص بك - {invited}/5",
        "price_suffix": "ج",
        "bundle_btn": "🔥 الباقة الكاملة 10 منتجات - 3000ج بدل 7000ج",
        "lang_btn": "🌐 Language / تغيير اللغة",
        "status_open": "✅ الهدية مفتوحة - دوس على الزرار وخدها!",
        "status_locked": "🔒 ضيف 5 أعضاء للقناة وخدها فوراً",
        "status_open_short": "✅ الهدية مفتوحة!",
        "status_locked_short": "🔒 ضيف 5 وخدها - عندك {invited}/5",
        "referral_notify": "🎉 حد جديد دخل من رابطك! بقى عندك {count}/5 دعوات. كمل 5 وخد الهدية!",
        "back": "⬅ رجوع للقائمة",
        "back_short": "⬅ رجوع",
        "gift_open_msg": "🎉 **مبروك! هديتك الفخمة جاهزة:**\n\n{link}\n\n📚 دليل 5 صفحات مصور\n- كيف تبيع على Gumroad\n- مصادر زيارات مجانية\n- خطة 7 أيام لأول مبيعة\n\n💡 الباقة الكاملة 10 منتجات بـ 3000ج بدل 7000ج - دوس /start",
        "gift_locked_msg": "🔒 **الهدية مقفولة!**\n\n📊 انت ضفت: {invited}/5 أعضاء\n\n**عشان تفتحها:**\n1. ادخل القناة\n2. ضيف 5 من صحابك (اعملهم Forward للقناة)\n3. خليهم يدوسوا على رابط الإحالة بتاعك\n4. ارجع دوس هنا\n\nشارك رابطك وهتاخدها أسرع!",
        "channel_btn": "📢 ادخل قناة Ghost Vault",
        "refresh_btn": "🔄 حدث العداد ({invited}/5)",
        "my_ref_btn": "💰 هات رابط الإحالة بتاعي",
        "referral_msg": "💰 **رابطك الخاص للإحالة:**\n\n`{link}`\n\nكل واحد يدخل من رابطك = 1 نقطة\n📊 عندك حاليا: {invited}/5\n\n🎁 5 نقاط = تاخد دليل Gumroad (1000ج)\n🔥 10 نقاط = تاخد كورس هدية\n💸 20 نقطة = قالب متجر الكتروني برمجه خاصه مجانا على بلوجر!\n\nشاركه في جروبات المصممين والربح من الانترنت!",
        "gift_progress_btn": "🎁 شوف هدفي ({invited}/5)",
        "paid_btn": "✅ حولت {price}ج - هبعت السكرين",
        "paypal_btn": "🌍 ادفع بـ PayPal — تحميل فوري بعد الدفع",
        "buy_paypal_line": "\n━━━━━━━━━━━━\n🌍 **أو ادفع بـ PayPal** من الزرار اللي تحت — بعد الدفع هتتحول **مباشرة لصفحة التحميل**.",
        "paid_prompt": "📸 **تمام! ابعت السكرين دلوقتي**\n\n⚠ **مهم:** اكتب مع الصورة اسم المنتج:\n`{name}`\n\nمثال: ابعت الصورة وفي الكابشن اكتب `{name}`",
        "bundle_paid_btn": "✅ حولت 3000ج - هبعت السكرين",
        "photo_ack": "✅ **تم استلام السكرين!**\n\n📦 المنتج: **{product}**\n⏳ جاري المراجعة وهيوصلك الرابط خلال دقائق",
        "deliver_single": "🎉 **تم تأكيد دفع {price}ج**\n\n📦 {name}\n📝 {desc}\n\n🔗 **رابط التحميل:**\n{link}\n\n💡 الرابط مدى الحياة\nشكراً لثقتك ❤",
        "deliver_bundle": "🎉 **مبروك! تم تأكيد دفع الباقة 3000ج**\n\n{links}\n\n💡 كل الروابط مدى الحياة\nشكراً لثقتك في Global Courses ❤",
        "reject_msg": "❌ السكرين مرفوض - مش واضح أو المبلغ غلط\n\nابعت سكرين واضح من تطبيق فودافون كاش + اكتب اسم المنتج\nأو كلمنا: @waheed_elfar",
        "hotgpt_btn": "🔥 HotGPT — اشتراك ذكاء اصطناعي",
        "gumroad_btn": "🛒 متجر Gumroad — كورسات ومكتبات",
        "hotgpt_text": "🔥 **HotGPT — ذكاء اصطناعي بلا حدود في البرمجة**\n\n✅ **نماذج حرة بدون قيود على كتابة أي كود برمجي**\n✅ أدوات متخصصة: فحص أمني، هندسة عكسية، تدقيق SEO، استخراج عملاء محتملين، ومنشئ مواقع كامل\n\n💳 اشتراك شهري **٢ دولار** بس — بايبال أو فودافون كاش أو إنستا باي\n\n👇 اشترك من الموقع:",
        "hotgpt_site_btn": "🌐 اشترك الآن — hotgpt.pro",
        "gumroad_text": "🛒 **متجر ORVNZA Studio على Gumroad**\n\nكورسات ومكتبات رقمية — دفع بالبطاقة وتحميل فوري من Gumroad نفسه.\n\n👇 اختر منتجًا أو افتح المتجر كله:",
        "gumroad_store_btn": "🏬 كل المنتجات على Gumroad",
    },
    "en": {
        "gift_btn": "🎁 Your free gift - Gumroad guide ({invited}/5)",
        "ref_btn": "💰 Your referral link - {invited}/5",
        "price_suffix": " EGP",
        "bundle_btn": "🔥 Full bundle: 10 products - 3000 EGP instead of 7000",
        "lang_btn": "🌐 اللغة / Language",
        "status_open": "✅ Your gift is unlocked - tap the button and grab it!",
        "status_locked": "🔒 Invite 5 members to the channel and grab it instantly",
        "status_open_short": "✅ Gift unlocked!",
        "status_locked_short": "🔒 Invite 5 to unlock - you have {invited}/5",
        "referral_notify": "🎉 Someone new joined from your link! You now have {count}/5 invites. Reach 5 and claim your gift!",
        "back": "⬅ Back to menu",
        "back_short": "⬅ Back",
        "gift_open_msg": "🎉 **Congrats! Your premium gift is ready:**\n\n{link}\n\n📚 5-page illustrated guide (in Arabic)\n- How to sell on Gumroad\n- Free traffic sources\n- A 7-day plan to your first sale\n\n💡 The full bundle: 10 products for 3000 EGP instead of 7000 - tap /start",
        "gift_locked_msg": "🔒 **Gift locked!**\n\n📊 You invited: {invited}/5 members\n\n**To unlock it:**\n1. Join the channel\n2. Invite 5 friends (forward the channel to them)\n3. They tap your referral link\n4. Come back and tap here\n\nShare your link and you will get it faster!",
        "channel_btn": "📢 Join the Ghost Vault channel",
        "refresh_btn": "🔄 Refresh counter ({invited}/5)",
        "my_ref_btn": "💰 Get my referral link",
        "referral_msg": "💰 **Your personal referral link:**\n\n`{link}`\n\nEveryone who joins from your link = 1 point\n📊 You currently have: {invited}/5\n\n🎁 5 points = the Gumroad guide (1000 EGP value)\n🔥 10 points = a free course\n💸 20 points = a free custom-coded Blogger store template!\n\nShare it in designer and online-income groups!",
        "gift_progress_btn": "🎁 My goal ({invited}/5)",
        "paid_btn": "✅ I transferred {price} EGP - sending the screenshot",
        "paypal_btn": "🌍 Pay with PayPal — instant download after payment",
        "buy_paypal_line": "",
        "paid_prompt": "📸 **Great! Send the screenshot now**\n\n⚠ **Important:** write the product name with the photo:\n`{name}`\n\nExample: send the photo and put `{name}` in the caption",
        "bundle_paid_btn": "✅ I transferred 3000 EGP - sending the screenshot",
        "photo_ack": "✅ **Screenshot received!**\n\n📦 Product: **{product}**\n⏳ Under review - your link arrives within minutes",
        "deliver_single": "🎉 **Your {price} EGP payment is confirmed!**\n\n📦 {name}\n📝 {desc}\n\n🔗 **Download link:**\n{link}\n\n💡 Lifetime access\nThanks for trusting us ❤",
        "deliver_bundle": "🎉 **Congrats! Your bundle payment (3000 EGP) is confirmed!**\n\n{links}\n\n💡 All links are lifetime access\nThanks for trusting Global Courses ❤",
        "reject_msg": "❌ Screenshot rejected - unclear or wrong amount\n\nSend a clear screenshot from the Vodafone Cash app + write the product name\nOr contact us: @waheed_elfar",
        "hotgpt_btn": "🔥 HotGPT — AI subscription",
        "gumroad_btn": "🛒 Gumroad store — courses & libraries",
        "hotgpt_text": "🔥 **HotGPT — AI that never blocks your code**\n\n✅ **Free, unrestricted models for writing any programming code**\n✅ Plus specialized tools: security scan, reverse engineering, SEO audit, lead extraction and a full site builder\n\n💳 Just **$2/month** via PayPal\n\n👇 Get it on the site:",
        "hotgpt_site_btn": "🌐 Subscribe now — hotgpt.pro",
        "gumroad_text": "🛒 **ORVNZA Studio on Gumroad**\n\nDigital courses, templates and tools — card payment with instant download via Gumroad.\n\n👇 Pick a product or open the full store:",
        "gumroad_store_btn": "🏬 All products on Gumroad",
    },
}

GUMROAD_AR = [
    ("📄 مكتبة العقود المصرية — $7", "https://orvnza.gumroad.com/l/torzvb"),
    ("📊 5000 شيت إكسيل جاهز — $9", "https://orvnza.gumroad.com/l/bgudpi"),
    ("💰 كورس CPA الكامل — $7", "https://orvnza.gumroad.com/l/pcvjq"),
    ("📣 إعلانات فيسبوك وإنستجرام — $10", "https://orvnza.gumroad.com/l/pnnjk"),
    ("🎯 باقة الإعلانات الشاملة — $15", "https://orvnza.gumroad.com/l/opuzrz"),
    ("🎨 فوتوشوب للمبتدئين — $7", "https://orvnza.gumroad.com/l/lwvjhb"),
    ("🖌 تصميم سوشيال ميديا متقدم — $7", "https://orvnza.gumroad.com/l/rmdidn"),
]
GUMROAD_EN = [
    ("🍽 Restaurant Menu Template — $40", "https://orvnza.gumroad.com/l/global-cafe-menu"),
    ("🚗 ONYX Car Showcase Template — $35", "https://orvnza.gumroad.com/l/sitecar"),
    ("🏠 Lotus Real Estate Site — $30", "https://orvnza.gumroad.com/l/luxurysite"),
    ("🛒 SMART SHOP X v2 Template — $15", "https://orvnza.gumroad.com/l/nxovia"),
    ("🎨 Smart Design Studio — $7", "https://orvnza.gumroad.com/l/smartdesignstudio"),
    ("📣 AI Commercial Prompt Pack — $5", "https://orvnza.gumroad.com/l/luxaiads"),
]

def T(lang, key, **kw):
    txt = TEXTS[lang][key]
    return txt.format(**kw) if kw else txt

def main_menu(user_id=None, invited=0, lang="ar"):
    kb = []
    # زرار الهدية الفيروسية أول واحد
    kb.append([InlineKeyboardButton(T(lang, "gift_btn", invited=invited), callback_data="gift")])
    kb.append([InlineKeyboardButton(T(lang, "ref_btn", invited=invited), callback_data="my_referral")])
    # كل لغة باللي يخصها: الإنجليزي يعرض فقط منتجات بايبال (تحميل فوري)،
    # والعربي يعرض الكتالوج الكامل بفودافون كاش + بايبال حيثما وجد.
    if lang == "en":
        kb.extend([[InlineKeyboardButton(pname(p, lang), callback_data=f"buy_{k}")] for k, p in PRODUCTS.items() if p.get("paypal")])
    else:
        kb.extend([[InlineKeyboardButton(f"{pname(p, lang)} - {p['price']}{T(lang, 'price_suffix')}", callback_data=f"buy_{k}")] for k, p in PRODUCTS.items()])
        kb.append([InlineKeyboardButton(T(lang, "bundle_btn"), callback_data="bundle")])
    kb.append([InlineKeyboardButton(T(lang, "hotgpt_btn"), callback_data="hotgpt")])
    kb.append([InlineKeyboardButton(T(lang, "gumroad_btn"), callback_data="gumroad")])
    kb.append([InlineKeyboardButton(T(lang, "lang_btn"), callback_data="lang_menu")])
    return InlineKeyboardMarkup(kb)

WELCOME_TEXT_TEMPLATE = """
🌍 **أهلاً بيك في Global Courses** 🌍
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
وبعض المنتجات تقدر تدفعها بـ PayPal وتحمّل فورًا

👇 **اختار من القائمة:**
"""

WELCOME_TEXT_TEMPLATE_EN = """
🌍 **Welcome to Global Courses** 🌍
The #1 digital products store

━━━━━━━━━━━━━━━━━━━━
🎁 **Your free gift (1000 EGP value):**
The Gumroad digital-products selling guide
5 illustrated pages - a 7-day plan to your first sale

📊 You invited: {invited}/5 members
{status}

━━━━━━━━━━━━━━━━━━━━
🎬 **Every course includes:**
✅ High-quality recorded videos
✅ Instant download after payment - lifetime access
✅ Free updates forever

🛒 **Store templates:**
✅ 100% exclusive templates - not sold anywhere else

━━━━━━━━━━━━━━━━━━━━
💳 **Payment:**
PayPal — instant download right after payment

👇 **Choose from the menu:**
"""

def welcome_text(lang, invited, status):
    tpl = WELCOME_TEXT_TEMPLATE_EN if lang == "en" else WELCOME_TEXT_TEMPLATE
    return tpl.format(invited=invited, status=status, payment=PAYMENT_NUMBER)

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
            invited_list = data[referrer].get("invited_list", [])
            if user_id not in invited_list:
                invited_list.append(user_id)
                data[referrer]["invited"] = len(invited_list)
                data[referrer]["invited_list"] = invited_list
                ref_lang = get_lang(data, referrer)
                try:
                    await context.bot.send_message(chat_id=int(referrer), text=T(ref_lang, "referral_notify", count=len(invited_list)))
                except:
                    pass
        save_data(data)

    if user_id not in data:
        data[user_id] = {"invited": 0, "got_gift": False, "invited_list": []}
        save_data(data)

    # اختيار اللغة لأول مرة
    if not data.get(user_id, {}).get("lang"):
        await update.message.reply_text("🌍 **Global Courses** 🌍\n\nاختر لغتك 👇\nChoose your language 👇", reply_markup=LANG_CHOOSER_MARKUP, parse_mode='Markdown')
        return

    lang = get_lang(data, user_id)
    invited = data.get(user_id, {}).get("invited", 0)
    got_gift = data.get(user_id, {}).get("got_gift", False)
    status = T(lang, "status_open") if invited >= 5 or got_gift else T(lang, "status_locked")

    text = welcome_text(lang, invited, status)
    await update.message.reply_text(text, reply_markup=main_menu(user_id, invited, lang), parse_mode='Markdown')

def render_welcome(lang, db, uid_str):
    invited = db.get(uid_str, {}).get("invited", 0)
    got_gift = db.get(uid_str, {}).get("got_gift", False)
    status = T(lang, "status_open_short") if invited >= 5 or got_gift else T(lang, "status_locked_short", invited=invited)
    return welcome_text(lang, invited, status), main_menu(uid_str, invited, lang)

async def btn_handler(update, context):
    q = update.callback_query
    await q.answer()
    data_str = q.data
    uid = q.from_user.id
    uid_str = str(uid)

    # أدمن - الموافقة (رسالة التسليم بلغة العميل)
    if uid == ADMIN_ID and data_str.startswith("approve_"):
        _, target_id, prod_key = data_str.split("_", 2)
        target_id = int(target_id)
        try:
            db0 = load_data()
            buyer_lang = get_lang(db0, str(target_id))
            if prod_key == "bundle":
                links = "\n\n".join([f"✅ {pname(v, buyer_lang)}:\n{v['link']}" for v in PRODUCTS.values()])
                msg = T(buyer_lang, "deliver_bundle", links=links)
            else:
                p = PRODUCTS[prod_key]
                msg = T(buyer_lang, "deliver_single", price=p['price'], name=pname(p, buyer_lang), desc=pdesc(p, buyer_lang), link=p['link'])
            await context.bot.send_message(chat_id=target_id, text=msg, parse_mode='Markdown')
            await q.edit_message_caption(caption=q.message.caption + f"\n\n✅ تم إرسال {PRODUCTS.get(prod_key, {'name':'الباقة'}).get('name','الباقة')}")
        except Exception as e:
            await q.answer(f"خطأ: {e}", show_alert=True)
        return

    if uid == ADMIN_ID and data_str.startswith("reject_"):
        target_id = int(data_str.split("_")[1])
        db0 = load_data()
        buyer_lang = get_lang(db0, str(target_id))
        await context.bot.send_message(chat_id=target_id, text=T(buyer_lang, "reject_msg"))
        await q.edit_message_caption(caption=q.message.caption + "\n\n❌ مرفوض")
        return

    # تحميل البيانات
    db = load_data()
    invited = db.get(uid_str, {}).get("invited", 0)

    # اختيار / تغيير اللغة
    if data_str == "lang_menu":
        await q.edit_message_text("🌍 **Global Courses** 🌍\n\nاختر لغتك 👇\nChoose your language 👇", reply_markup=LANG_CHOOSER_MARKUP, parse_mode='Markdown')
        return
    if data_str in ("lang_ar", "lang_en"):
        lang = "ar" if data_str == "lang_ar" else "en"
        if uid_str not in db:
            db[uid_str] = {"invited": 0, "got_gift": False, "invited_list": []}
        db[uid_str]["lang"] = lang
        save_data(db)
        text, markup = render_welcome(lang, db, uid_str)
        await q.edit_message_text(text, reply_markup=markup, parse_mode='Markdown')
        return

    lang = get_lang(db, uid_str)

    if data_str == "gift":
        if invited >= 5 or db.get(uid_str, {}).get("got_gift"):
            db[uid_str]["got_gift"] = True
            save_data(db)
            await q.message.reply_text(T(lang, "gift_open_msg", link=GIFT_LINK_AR), parse_mode='Markdown')
        else:
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(T(lang, "channel_btn"), url=CHANNEL_LINK)],
                [InlineKeyboardButton(T(lang, "refresh_btn", invited=invited), callback_data="gift")],
                [InlineKeyboardButton(T(lang, "my_ref_btn"), callback_data="my_referral")],
                [InlineKeyboardButton(T(lang, "back"), callback_data="back")]
            ])
            await q.message.reply_text(T(lang, "gift_locked_msg", invited=invited), reply_markup=markup, parse_mode='Markdown')

    elif data_str == "my_referral":
        referral_link = f"https://t.me/{BOT_USERNAME}?start={uid_str}"
        txt = T(lang, "referral_msg", link=referral_link, invited=invited)
        kb = [[InlineKeyboardButton(T(lang, "gift_progress_btn", invited=invited), callback_data="gift")], [InlineKeyboardButton(T(lang, "back_short"), callback_data="back")]]
        await q.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str.startswith("buy_"):
        k = data_str.replace("buy_", "")
        p = PRODUCTS[k]
        if lang == "en":
            txt = f"✅ **{pname(p, lang)}**\n\n📝 {pdesc(p, lang)}\n\n🌍 **Pay with PayPal** — tap the button below. Right after payment, PayPal redirects you **straight to your download**. Nothing else to send, no waiting."
        else:
            txt = f"✅ **{p['name']}**\n\n📝 {p['desc']}\n💰 السعر: {p['price']} جنيه\n\n━━━━━━━━━━━━\n💳 **حول {p['price']}ج على:**\n`{PAYMENT_NUMBER}`\n\n📸 **بعد التحويل:**\nابعت سكرين شوت + اكتب معاه:\n`{p['name']}`"
            if p.get("paypal"):
                txt += T(lang, "buy_paypal_line")
        if lang == "en":
            kb = []
            if p.get("paypal"):
                kb.append([InlineKeyboardButton(T(lang, "paypal_btn"), url=p["paypal"])])
            kb.append([InlineKeyboardButton(T(lang, "back"), callback_data="back")])
        else:
            kb = [[InlineKeyboardButton(T(lang, "paid_btn", price=p['price']), callback_data=f"paid_{k}")]]
            if p.get("paypal"):
                kb.append([InlineKeyboardButton(T(lang, "paypal_btn"), url=p["paypal"])])
            kb.append([InlineKeyboardButton(T(lang, "back"), callback_data="back")])
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str.startswith("paid_"):
        k = data_str.replace("paid_", "")
        prod_name = pname(PRODUCTS[k], lang) if k in PRODUCTS else ("🔥 Full Bundle" if lang == "en" else "الباقة")
        await q.edit_message_text(T(lang, "paid_prompt", name=prod_name), parse_mode='Markdown', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(T(lang, "back_short"), callback_data="back")]]))

    elif data_str == "bundle":
        if lang == "en":
            txt = f"🔥 **Full Bundle - 10 products**\n\n💰 **3000 EGP instead of 7000** (57% off)\n\n📦 You get:\n- 7 recorded video courses\n- 3 exclusive templates\n\n💳 **Transfer 3000 EGP to:**\n`{PAYMENT_NUMBER}`\n\n📸 Then send the screenshot with `Bundle` in the caption"
        else:
            txt = f"🔥 **الباقة الكاملة - 10 منتجات**\n\n💰 **3000ج بدل 7000ج** (خصم 57%)\n\n📦 هتاخد:\n- 7 كورسات فيديو مسجلة\n- 3 قوالب خاصة بينا\n\n💳 **حول 3000ج على:**\n`{PAYMENT_NUMBER}`\n\n📸 بعدها ابعت السكرين + اكتب `الباقة`"
        kb = [[InlineKeyboardButton(T(lang, "bundle_paid_btn"), callback_data="paid_bundle")], [InlineKeyboardButton(T(lang, "back"), callback_data="back")]]
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str == "hotgpt":
        kb = [[InlineKeyboardButton(T(lang, "hotgpt_site_btn"), url="https://hotgpt.pro")], [InlineKeyboardButton(T(lang, "back"), callback_data="back")]]
        await q.edit_message_text(T(lang, "hotgpt_text"), reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str == "gumroad":
        items = GUMROAD_EN if lang == "en" else GUMROAD_AR
        kb = [[InlineKeyboardButton(label, url=url)] for label, url in items]
        kb.append([InlineKeyboardButton(T(lang, "gumroad_store_btn"), url="https://orvnza.gumroad.com")])
        kb.append([InlineKeyboardButton(T(lang, "back"), callback_data="back")])
        await q.edit_message_text(T(lang, "gumroad_text"), reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

    elif data_str == "back":
        db = load_data()
        text, markup = render_welcome(get_lang(db, uid_str), db, uid_str)
        await q.edit_message_text(text, reply_markup=markup, parse_mode='Markdown')

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
    for k, p in PRODUCTS.items():
        kb_rows.append([InlineKeyboardButton(f"✅ {p['name']} ({p['price']}ج)", callback_data=f"approve_{user.id}_{k}")])
    kb_rows.append([InlineKeyboardButton("✅🔥 الباقة (3000ج)", callback_data=f"approve_{user.id}_bundle")])
    kb_rows.append([InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")])

    try:
        if is_document:
            await context.bot.send_document(chat_id=ADMIN_ID, document=photo_file_id, caption=caption_text, reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode='Markdown')
        else:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption=caption_text, reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode='Markdown')
        db = load_data()
        user_lang = get_lang(db, str(user.id))
        await update.message.reply_text(T(user_lang, "photo_ack", product=guessed_product), parse_mode='Markdown')
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
    return "Bot is running! Global Courses - Viral Gift"

@flask_app.route('/api', methods=['POST', 'GET'])
@flask_app.route('/api/index', methods=['POST', 'GET'])
@flask_app.route('/', methods=['POST'])
def webhook():
    if request.method == 'GET':
        return "Bot is running! Global Courses - Viral"
    try:
        data = request.get_json(force=True)
        asyncio.run(process_update(data))
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return f"Error: {e}", 200

app = flask_app
