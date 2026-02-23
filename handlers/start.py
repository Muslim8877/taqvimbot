from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.language import language_selector
    await language_selector(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('language', 'uz_latin')

    texts = {
        'uz_latin': {
            'welcome': "Assalomu alaykum! 👋",
            'menu': "Quyidagilardan birini tanlang:",
            'namoz': "🕌 Namoz vaqtlari",
            'masjid': "📍 Eng yaqin masjid",
            'iftar': "🌙 Roza vaqtlari",
            'pdf': "📸 Rasm → PDF",
        },
        'uz_kiril': {
            'welcome': "Ассалому алайкум! 👋",
            'menu': "Қуйидагилардан бирини танланг:",
            'namoz': "🕌 Намоз вақтлари",
            'masjid': "📍 Энг яқин масжид",
            'iftar': "🌙 Роза вақтлари",
            'pdf': "📸 Расм → PDF",
        },
        'en': {
            'welcome': "Hello! 👋",
            'menu': "Choose one:",
            'namoz': "🕌 Prayer times",
            'masjid': "📍 Nearest mosque",
            'iftar': "🌙 Fasting times",
            'pdf': "📸 Image → PDF",
        }
    }

    t = texts.get(lang, texts['uz_latin'])

    keyboard = [
        [InlineKeyboardButton(t['namoz'], callback_data='namoz')],
        [InlineKeyboardButton(t['masjid'], callback_data='masjid')],
        [InlineKeyboardButton(t['iftar'], callback_data='iftar')],
        [InlineKeyboardButton(t['pdf'], callback_data='pdf')],
        [InlineKeyboardButton("🌐 Til", callback_data='change_language')]
    ]

    await query.edit_message_text(
        f"{t['welcome']}\n\n{t['menu']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )