import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
from config import BOT_TOKEN
from keyboards import main_menu_kb
from handlers import (
    handle_order, receive_ign, receive_ss, handle_confirmation, handle_admin_action,
    admin_show_orders, user_show_orders
)

logging.basicConfig(level=logging.INFO)

async def start(update, context):
    await update.message.reply_text("မင်္ဂလာပါ! 💎 ML Diamond ဝယ်ရန်:", reply_markup=main_menu_kb())

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", admin_show_orders))
    app.add_handler(CommandHandler("myorders", user_show_orders))

    app.add_handler(CallbackQueryHandler(handle_order, pattern="^(cat_|prod_|pay_|back_main)"))
    app.add_handler(CallbackQueryHandler(handle_confirmation, pattern="^(confirm_order|cancel_order)$"))
    app.add_handler(CallbackQueryHandler(handle_admin_action, pattern="^(approve_|decline_)"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ign))
    app.add_handler(MessageHandler(filters.PHOTO, receive_ss))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
