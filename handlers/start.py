from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi - til tanlashga o'tkazadi"""
    from handlers.language import language_selector
    await language_selector(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyuni ko'rsatish"""
    query = update.callback_query
    lang = context.user_data.get('language', 'uz_latin')

    # Matnlar
    texts = {
        'uz_latin': {
            'welcome': "Assalomu alaykum! 👋",
            'namoz': "🕌 Namoz vaqtlari",
            'iftar': "🌙 Roza vaqtlari",
            'masjid': "📍 Eng yaqin masjid",
            'pdf': "📸 Rasm → PDF",
        },
        'uz_kiril': {
            'welcome': "Ассалому алайкум! 👋",
            'namoz': "🕌 Намоз вақтлари",
            'iftar': "🌙 Роза вақтлари",
            'masjid': "📍 Энг яқин масжид",
            'pdf': "📸 Расм → PDF",
        },
        'en': {
            'welcome': "Hello! 👋",
            'namoz': "🕌 Prayer times",
            'iftar': "🌙 Fasting times",
            'masjid': "📍 Nearest mosque",
            'pdf': "📸 Image → PDF",
        }
    }

    t = texts.get(lang, texts['uz_latin'])

    # Tugmalar (5 ta)
    keyboard = [
        [InlineKeyboardButton(t['namoz'], callback_data='namoz')],
        [InlineKeyboardButton(t['iftar'], callback_data='iftar')],
        [InlineKeyboardButton(t['masjid'], callback_data='masjid')],
        [InlineKeyboardButton(t['pdf'], callback_data='pdf')],
        [InlineKeyboardButton("🌐 Til", callback_data='change_language')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"{t['welcome']}\n\nTanlang:",
        reply_markup=reply_markup
    )