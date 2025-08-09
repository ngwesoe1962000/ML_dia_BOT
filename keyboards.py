from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from products import PRODUCT_CATEGORIES, PAYMENT_METHODS

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(cat, callback_data=f"cat_{cat}")]
        for cat in PRODUCT_CATEGORIES
    ])

def products_kb(category):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(p, callback_data=f"prod_{data}")]
        for p, data in PRODUCT_CATEGORIES[category].items()
    ] + [[InlineKeyboardButton("🔙 နောက်သို့", callback_data="back_main")]])

def payment_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(method, callback_data=f"pay_{method}")]
        for method in PAYMENT_METHODS
    ])

def confirm_order_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ အတည်ပြု", callback_data="confirm_order"),
         InlineKeyboardButton("❌ ပယ်ဖျက်မည်", callback_data="cancel_order")]
    ])

def approve_kb(order_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ အတည်ပြု", callback_data=f"approve_{order_id}"),
         InlineKeyboardButton("❌ ငြင်းပယ်", callback_data=f"decline_{order_id}")]
    ])
