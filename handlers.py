from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID, ORDER_CHANNEL, PAYMENT_INFO
from keyboards import *
import json
import uuid

ORDERS_FILE = "orders.json"

def load_orders():
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_order(order):
    orders = load_orders()
    order_id = str(uuid.uuid4())[:8]
    orders[order_id] = order
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    return order_id

# Step-by-step order flow
async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_data = context.user_data

    if data.startswith("cat_"):
        cat = data[4:]
        user_data["category"] = cat
        await query.edit_message_text(f"📦 {cat} မှ ရွေးပါ။", reply_markup=products_kb(cat))

    elif data.startswith("prod_"):
        prod = data[5:]
        user_data["product"] = prod
        await query.edit_message_text("💳 ငွေပေးချေမှုနည်းလမ်း ရွေးပါ။", reply_markup=payment_kb())

    elif data.startswith("pay_"):
        payment = data[4:]
        user_data["payment"] = payment
        await query.edit_message_text("🎮 In-game ID & Name ကို '12345678(1234) Mg Mg' ပုံစံနဲ့ ရိုက်ထည့်ပါ။\n\n📌 မှန်ကန်စွာ သေချာစစ်ဆေးပြီးမှ ထည့်ပေးပါ။ အမှားအယွင်းဖြစ်ပါက ငွေပြန်အမ်းပေးမည် မဟုတ်ပါ။\n\n📌 မှားယွင်းသွားခဲ့လျှင်လဲ ချက်ချင်း @T7sensai ကိုဆက်သွယ်ပြီး ပြောထားပေးပါ။")
        user_data["awaiting_ign"] = True

    elif data == "back_main":
        await query.edit_message_text("မင်္ဂလာပါ! 💎 ML Diamond ဝယ်ရန် အောက်ပါများမှ ရွေးချယ်ပေးပါ:", reply_markup=main_menu_kb())

async def receive_ign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_ign"):
        return
    context.user_data["ign"] = update.message.text
    context.user_data["awaiting_ign"] = False
    context.user_data["awaiting_ss"] = True
    await update.message.reply_text(f"📸 ငွေပေးချေပြီး screenshot ပေးပို့ပါ။\n\n📌ပြေစာတွင် transaction ID ပါအောင်ရိုက်ပေးပါ\n\n📌Note တွင် နာမည်ရှေ့စာလုံး ထည့်ပေးပါ\n\n📌မှားယွင်းလွှဲမိမှုများအတွက် တာဝန်မယူပါ\n\n📌 {PAYMENT_INFO}")

async def receive_ss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_ss"):
        return
    if not update.message.photo:
        await update.message.reply_text("ဓာတ်ပုံပေးပို့ရန်လိုအပ်ပါသည်။")
        return
    file_id = update.message.photo[-1].file_id
    context.user_data["ss_photo"] = file_id
    context.user_data["awaiting_ss"] = False

    preview = (
        f"📦 ပစ္စည်း: {context.user_data['product']}\n"
        f"💳 ငွေပေးချေမှု: {context.user_data['payment']}\n"
        f"🎮 IGN: {context.user_data['ign']}\n"
        f"📸 Screenshot တင်ပြီးပါပြီ။"
    )

    await update.message.reply_photo(
        photo=file_id,
        caption=preview + "\n\n✅ အော်ဒါအတည်ပြုမလား?",
        reply_markup=confirm_order_kb()
    )

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = context.user_data

    if query.data == "confirm_order":
        order = {
            "user_id": user.id,
            "username": user.username,
            "product": data["product"],
            "payment": data["payment"],
            "ign": data["ign"],
            "photo": data["ss_photo"]
        }

        order_id = save_order(order)

        msg = (
            f"📥 အသစ်အော်ဒါ\n"
            f"👤 @{user.username} (ID: {user.id})\n"
            f"📦 ပစ္စည်း: {data['product']}\n"
            f"💳 ငွေပေးချေမှု: {data['payment']}\n"
            f"🎮 IGN: {data['ign']}\n"
            f"🆔 Order ID: {order_id}"
        )

        await context.bot.send_photo(chat_id=ADMIN_ID, photo=data["ss_photo"], caption=msg, reply_markup=approve_kb(order_id))
        await context.bot.send_photo(chat_id=ORDER_CHANNEL, photo=data["ss_photo"], caption=msg)
        await query.edit_message_caption("📦 အော်ဒါကို အောင်မြင်စွာ ပေးလိုက်ပါပြီ။ ကျေးဇူးတင်ပါတယ်။\n\nသင့်အော်ဒါများကို ချန်နယ်ထဲတွင် အချိန်မရွေးဝင်ရောက်ကြည့်ရှုစစ်ဆေးနိုင်ပါတယ်။ ချန်နယ် - https://t.me/orderchannelkakashi \n\nထပ်မံရွေးချယ်ဝယ်ယူလိုပါက /start ကိုနှိပ်ပါ")
        context.user_data.clear()

    elif query.data == "cancel_order":
        await query.edit_message_caption("❌ အော်ဒါကို ပယ်ဖျက်လိုက်ပါပြီ။\n\nထပ်မံရွေးချယ်ဝယ်ယူလိုပါက /start ကိုနှိပ်ပါ")
        context.user_data.clear()

async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("approve_") or data.startswith("decline_"):
        action, oid = data.split("_")
        orders = load_orders()
        order = orders.get(oid)
        if not order:
            await query.answer("Order မတွေ့ပါ။")
            return

        uid = order["user_id"]
        if action == "approve":
            await context.bot.send_message(chat_id=uid, text="✅ သင့်အော်ဒါကို အတည်ပြုလိုက်ပါပြီ။\n\nGame ထဲဝင်ပြီး Diamond ရောက်မရောက် စစ်ဆေးပြီး ပြဿနာတစ်စုံတစ်ရာရှိပါက @T7sensai ကိုဆက်သွယ်ပေးပါ\n\nထပ်မံရွေးချယ်ဝယ်ယူလိုပါက /start ကိုနှိပ်ပါ")
            await query.edit_message_caption(caption="✅ Order Approved")
        else:
            await context.bot.send_message(chat_id=uid, text="❌ သင့်အော်ဒါကို ငြင်းပယ်လိုက်ပါသည်။\n\nတစ်စုံတစ်ခုမှားယွင်းမှု ကြောင့်ဖြစ်နိုင်ပါတယ်။\n\nအထူးသဖြင့် game id နှင့် name ကိုသေချာပြန်စစ်ဆေးပါ။ \n\nငွေလွှဲပြေစာကို စစ်ဆေးပါ\n\n\n\nထပ်မံရွေးချယ်ဝယ်ယူလိုပါက /start ကိုနှိပ်ပါ")
            await query.edit_message_caption(caption="❌ Order Declined")

# Admin command to show all orders
async def admin_show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ သင်သည် Admin မဟုတ်ပါ။ ")
        return

    orders = load_orders()
    if not orders:
        await update.message.reply_text("📭 အော်ဒါ မရှိသေးပါ။")
        return

    text = "📋 အားလုံးအော်ဒါများ\n\n"
    for oid, order in orders.items():
        text += (
            f"🆔 {oid}\n"
            f"👤 @{order.get('username', 'unknown')}\n"
            f"📦 {order['product']}\n"
            f"💳 {order['payment']}\n"
            f"🎮 IGN: {order['ign']}\n\n"
        )
    await update.message.reply_text(text)

# User command to show own orders
async def user_show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    orders = load_orders()

    user_orders = {oid: o for oid, o in orders.items() if o.get("user_id") == user_id}
    if not user_orders:
        await update.message.reply_text("📭 သင်၏အော်ဒါ မရှိသေးပါ။")
        return

    text = "🛒 သင့်အော်ဒါများ\n\n"
    for oid, order in user_orders.items():
        text += (
            f"🆔 {oid}\n"
            f"📦 {order['product']}\n"
            f"💳 {order['payment']}\n"
            f"🎮 IGN: {order['ign']}\n\n"
        )
    await update.message.reply_text(text)
