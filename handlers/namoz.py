from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.prayer_times import VILOYATLAR, get_namoz_vaqtlari, format_namoz_vaqtlari


async def namoz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Viloyat tanlash menyusi"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    # Tugmalarni yaratish (3 qatorli)
    keyboard = []
    row = []
    for i, viloyat in enumerate(VILOYATLAR):
        row.append(InlineKeyboardButton(viloyat, callback_data=f"viloyat_{viloyat}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    # Ortga tugmasi
    back_text = {
        'uz_latin': "🔙 Asosiy menyu",
        'uz_kiril': "🔙 Асосий меню",
        'en': "🔙 Main menu"
    }.get(lang, "🔙 Asosiy menyu")

    keyboard.append([InlineKeyboardButton(back_text, callback_data="back_to_menu")])

    # Sarlavha
    title = {
        'uz_latin': "🌍 Viloyatni tanlang:",
        'uz_kiril': "🌍 Вилоятни танланг:",
        'en': "🌍 Choose region:"
    }.get(lang, "🌍 Viloyatni tanlang:")

    await query.edit_message_text(title, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_namoz_vaqtlari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tanlangan viloyat namoz vaqtlarini ko‘rsatish"""
    query = update.callback_query
    await query.answer()

    viloyat = query.data.replace('viloyat_', '')
    lang = context.user_data.get('language', 'uz_latin')

    # Kutish xabari
    loading = {
        'uz_latin': f"⏳ {viloyat} uchun namoz vaqtlari olinmoqda...",
        'uz_kiril': f"⏳ {viloyat} учун намоз вақтлари олинмоқда...",
        'en': f"⏳ Getting prayer times for {viloyat}..."
    }.get(lang, f"⏳ {viloyat} uchun namoz vaqtlari olinmoqda...")

    await query.edit_message_text(loading)

    # Namoz vaqtlarini olish
    result = await get_namoz_vaqtlari(viloyat)

    if result["success"]:
        text = format_namoz_vaqtlari(result, lang)
    else:
        error_texts = {
            'uz_latin': "❌ Namoz vaqtlarini olishda xatolik yuz berdi.",
            'uz_kiril': "❌ Намоз вақтларини олишда хато юз берди.",
            'en': "❌ Error getting prayer times."
        }
        text = error_texts.get(lang, error_texts['uz_latin'])

    # Tugmalar
    keyboard = [
        [InlineKeyboardButton("🔄 Qaytadan", callback_data="namoz")],
        [InlineKeyboardButton("🔙 Viloyatlar", callback_data="namoz")],
        [InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )