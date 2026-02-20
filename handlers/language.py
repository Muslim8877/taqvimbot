from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def language_selector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek lotin", callback_data='lang_uz_latin')],
        [InlineKeyboardButton("🇺🇿 Ўзбек кирил", callback_data='lang_uz_kiril')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
    ]
    text = "🌐 Tilni tanlang:"

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.replace('lang_', '')
    context.user_data['language'] = lang
    from handlers.start import show_main_menu
    await show_main_menu(update, context)