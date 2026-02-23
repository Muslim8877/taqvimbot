from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.mosque_finder import find_masjid, format_masjid_list, format_masjid_detail
import logging

logger = logging.getLogger(__name__)


async def mosque_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    texts = {
        'uz_latin': "📍 <b>Joylashuvingizni yuboring</b>\n\n📎 → Joylashuv → Yuborish",
        'uz_kiril': "📍 <b>Жойлашувингизни юборинг</b>\n\n📎 → Жойлашув → Юбориш",
        'en': "📍 <b>Send your location</b>\n\n📎 → Location → Send"
    }

    keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]]

    await query.edit_message_text(
        texts.get(lang, texts['uz_latin']),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    context.user_data['waiting_for_location'] = True


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        location = update.message.location
        if not location:
            return

        lat, lon = location.latitude, location.longitude
        lang = context.user_data.get('language', 'uz_latin')

        loading = {
            'uz_latin': "⏳ Atrofingizdagi masjidlar qidirilmoqda...",
            'uz_kiril': "⏳ Атрофингиздаги масжидлар қидирилмоқда...",
            'en': "⏳ Searching for nearby mosques..."
        }

        msg = await update.message.reply_text(loading.get(lang, loading['uz_latin']))

        masjidlar = await find_masjid(lat, lon)
        await msg.delete()

        if masjidlar:
            text = format_masjid_list(masjidlar, lang)

            keyboard = []
            for i, m in enumerate(masjidlar[:5]):
                keyboard.append([InlineKeyboardButton(
                    f"{i + 1}. {m['name'][:30]}",
                    callback_data=f"mosque_{i}"
                )])

            keyboard.append([InlineKeyboardButton("🔄 Qaytadan", callback_data="masjid")])
            keyboard.append([InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")])

            context.user_data['last_mosques'] = masjidlar

            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        else:
            error = {
                'uz_latin': "❌ Atrofingizda masjid topilmadi.",
                'uz_kiril': "❌ Атрофингизда масжид топилмади.",
                'en': "❌ No mosques found nearby."
            }
            keyboard = [[InlineKeyboardButton("🔄 Qaytadan", callback_data="masjid")]]
            await update.message.reply_text(
                error.get(lang, error['uz_latin']),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        context.user_data['waiting_for_location'] = False

    except Exception as e:
        logger.error(f"Lokatsiya xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi.")


async def mosque_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    lang = context.user_data.get('language', 'uz_latin')

    if data == "mosque_back":
        masjidlar = context.user_data.get('last_mosques', [])
        if masjidlar:
            text = format_masjid_list(masjidlar, lang)

            keyboard = []
            for i, m in enumerate(masjidlar[:5]):
                keyboard.append([InlineKeyboardButton(
                    f"{i + 1}. {m['name'][:30]}",
                    callback_data=f"mosque_{i}"
                )])

            keyboard.append([InlineKeyboardButton("🔄 Qaytadan", callback_data="masjid")])
            keyboard.append([InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")])

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        return

    if data.startswith("mosque_"):
        idx = int(data.replace("mosque_", ""))
        masjidlar = context.user_data.get('last_mosques', [])

        if 0 <= idx < len(masjidlar):
            masjid = masjidlar[idx]
            text = format_masjid_detail(masjid, lang)

            back_text = {
                'uz_latin': "🔙 Ortga",
                'uz_kiril': "🔙 Ортга",
                'en': "🔙 Back"
            }.get(lang, "🔙 Ortga")

            keyboard = [[InlineKeyboardButton(back_text, callback_data="mosque_back")]]

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML',
                disable_web_page_preview=False
            )