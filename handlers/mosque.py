from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.mosque_finder import find_masjid, format_masjid_list, format_masjid_detail
import logging

logger = logging.getLogger(__name__)


async def mosque_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Masjid qidirishni boshlash"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    texts = {
        'uz_latin': "📍 <b>Joylashuvingizni yuboring</b>\n\n"
                    "📎 → Joylashuv → Yuborish",
        'uz_kiril': "📍 <b>Жойлашувингизни юборинг</b>\n\n"
                    "📎 → Жойлашув → Юбориш",
        'en': "📍 <b>Send your location</b>\n\n"
              "📎 → Location → Send"
    }

    keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]]

    await query.edit_message_text(
        texts.get(lang, texts['uz_latin']),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

    context.user_data['waiting_for_location'] = True


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lokatsiya qabul qilish va masjidlarni topish"""
    try:
        location = update.message.location
        if not location:
            return

        lat = location.latitude
        lon = location.longitude

        lang = context.user_data.get('language', 'uz_latin')

        # Kutish xabari
        loading_texts = {
            'uz_latin': "⏳ Atrofingizdagi masjidlar qidirilmoqda...",
            'uz_kiril': "⏳ Атрофингиздаги масжидлар қидирилмоқда...",
            'en': "⏳ Searching for nearby mosques..."
        }

        loading_msg = await update.message.reply_text(
            loading_texts.get(lang, loading_texts['uz_latin'])
        )

        # Masjidlarni qidirish
        masjidlar = await find_masjid(lat, lon)

        await loading_msg.delete()

        if masjidlar:
            text = format_masjid_list(masjidlar, lang)

            # Tugmalar yaratish
            keyboard = []
            for i, m in enumerate(masjidlar[:5]):
                button_text = f"{i + 1}. {m['name'][:30]}"
                keyboard.append([InlineKeyboardButton(
                    button_text,
                    callback_data=f"mosque_{i}"
                )])

            # Qaytadan va asosiy menyu
            back_texts = {
                'uz_latin': "🔄 Qaytadan qidirish",
                'uz_kiril': "🔄 Қайтадан қидириш",
                'en': "🔄 Search again"
            }
            menu_texts = {
                'uz_latin': "🔙 Asosiy menyu",
                'uz_kiril': "🔙 Асосий меню",
                'en': "🔙 Main menu"
            }

            keyboard.append([InlineKeyboardButton(back_texts.get(lang), callback_data="masjid")])
            keyboard.append([InlineKeyboardButton(menu_texts.get(lang), callback_data="back_to_menu")])

            # Masjidlarni saqlash
            context.user_data['last_mosques'] = masjidlar

            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        else:
            error_texts = {
                'uz_latin': "❌ Atrofingizda masjid topilmadi.\nBoshqa joylashuv yuborib ko'ring.",
                'uz_kiril': "❌ Атрофингизда масжид топилмади.\nБошқа жойлашув юбориб кўринг.",
                'en': "❌ No mosques found nearby.\nTry another location."
            }

            keyboard = [[InlineKeyboardButton("🔄 Qaytadan", callback_data="masjid")]]
            await update.message.reply_text(
                error_texts.get(lang),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        context.user_data['waiting_for_location'] = False

    except Exception as e:
        logger.error(f"Lokatsiya xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


async def mosque_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Masjid tugmalari bosilganda"""
    query = update.callback_query
    await query.answer()

    data = query.data
    lang = context.user_data.get('language', 'uz_latin')

    if data == "mosque_back":
        # Masjidlar ro'yxatiga qaytish
        masjidlar = context.user_data.get('last_mosques', [])
        if masjidlar:
            text = format_masjid_list(masjidlar, lang)

            keyboard = []
            for i, m in enumerate(masjidlar[:5]):
                button_text = f"{i + 1}. {m['name'][:30]}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"mosque_{i}")])

            back_texts = {
                'uz_latin': "🔄 Qaytadan qidirish",
                'uz_kiril': "🔄 Қайтадан қидириш",
                'en': "🔄 Search again"
            }
            menu_texts = {
                'uz_latin': "🔙 Asosiy menyu",
                'uz_kiril': "🔙 Асосий меню",
                'en': "🔙 Main menu"
            }

            keyboard.append([InlineKeyboardButton(back_texts.get(lang), callback_data="masjid")])
            keyboard.append([InlineKeyboardButton(menu_texts.get(lang), callback_data="back_to_menu")])

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        return

    if data.startswith("mosque_"):
        index = int(data.replace("mosque_", ""))
        masjidlar = context.user_data.get('last_mosques', [])

        if 0 <= index < len(masjidlar):
            masjid = masjidlar[index]
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