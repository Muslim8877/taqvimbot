from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.iftar_times import VILOYATLAR, get_roza_vaqtlari, format_roza_vaqtlari


async def iftar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('language', 'uz_latin')

    keyboard = []
    row = []
    for i, viloyat in enumerate(VILOYATLAR):
        row.append(InlineKeyboardButton(viloyat, callback_data=f"iftar_{viloyat}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    back_text = {
        'uz_latin': "🔙 Asosiy menyu",
        'uz_kiril': "🔙 Асосий меню",
        'en': "🔙 Main menu"
    }.get(lang, "🔙 Asosiy menyu")
    keyboard.append([InlineKeyboardButton(back_text, callback_data="back_to_menu")])

    title = {
        'uz_latin': "🌍 Viloyatni tanlang:",
        'uz_kiril': "🌍 Вилоятни танланг:",
        'en': "🌍 Choose region:"
    }.get(lang, "🌍 Viloyatni tanlang:")

    await query.edit_message_text(title, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_roza_vaqtlari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    viloyat = query.data.replace('iftar_', '')
    lang = context.user_data.get('language', 'uz_latin')

    loading = {
        'uz_latin': f"⏳ {viloyat} uchun roza vaqtlari olinmoqda...",
        'uz_kiril': f"⏳ {viloyat} учун роза вақтлари олинмоқда...",
        'en': f"⏳ Getting fasting times for {viloyat}..."
    }.get(lang, f"⏳ {viloyat} uchun roza vaqtlari olinmoqda...")

    await query.edit_message_text(loading)

    result = await get_roza_vaqtlari(viloyat)

    if result["success"]:
        text = format_roza_vaqtlari(result, lang)
    else:
        text = "❌ Roza vaqtlarini olishda xatolik."

    keyboard = [
        [InlineKeyboardButton("🔄 Qaytadan", callback_data="iftar")],
        [InlineKeyboardButton("🔙 Viloyatlar", callback_data="iftar")],
        [InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )