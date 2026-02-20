from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.weather import SHAHARLAR, get_weather_by_city, get_weather_by_location, format_weather
import os

# OpenWeatherMap API kaliti (buni .env fayliga qo'shish kerak)
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')


async def weather_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ob-havo menyusi"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    texts = {
        'uz_latin': {
            'title': "🌤 Ob-havo ma'lumoti",
            'city': "🏙 Shahar tanlash",
            'location': "📍 Lokatsiya yuborish",
            'back': "🔙 Asosiy menyu"
        },
        'uz_kiril': {
            'title': "🌤 Об-ҳаво маълумоти",
            'city': "🏙 Шаҳар танлаш",
            'location': "📍 Локатсия юбориш",
            'back': "🔙 Асосий меню"
        },
        'en': {
            'title': "🌤 Weather info",
            'city': "🏙 Choose city",
            'location': "📍 Send location",
            'back': "🔙 Main menu"
        }
    }

    t = texts.get(lang, texts['uz_latin'])

    keyboard = [
        [InlineKeyboardButton(t['city'], callback_data='weather_city_menu')],
        [InlineKeyboardButton(t['location'], callback_data='weather_location')],
        [InlineKeyboardButton(t['back'], callback_data='back_to_menu')]
    ]

    await query.edit_message_text(
        t['title'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def weather_city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shahar tanlash menyusi"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    # Tugmalar yaratish
    keyboard = []
    row = []
    for i, shahar in enumerate(SHAHARLAR):
        row.append(InlineKeyboardButton(shahar, callback_data=f"weather_city_{shahar}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    back_text = {
        'uz_latin': "🔙 Ortga",
        'uz_kiril': "🔙 Ортга",
        'en': "🔙 Back"
    }.get(lang, "🔙 Ortga")

    keyboard.append([InlineKeyboardButton(back_text, callback_data="weather")])

    title = {
        'uz_latin': "🌍 Shahar tanlang:",
        'uz_kiril': "🌍 Шаҳар танланг:",
        'en': "🌍 Choose city:"
    }.get(lang, "🌍 Shahar tanlang:")

    await query.edit_message_text(title, reply_markup=InlineKeyboardMarkup(keyboard))


async def weather_location_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lokatsiya so'rash"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    texts = {
        'uz_latin': "📍 Iltimos, joylashuvingizni yuboring\n\n📎 → Joylashuv → Yuborish",
        'uz_kiril': "📍 Илтимос, жойлашувингизни юборинг\n\n📎 → Жойлашув → Юбориш",
        'en': "📍 Please send your location\n\n📎 → Location → Send"
    }

    keyboard = [[InlineKeyboardButton("🔙 Ortga", callback_data="weather")]]

    context.user_data['waiting_for_weather_location'] = True

    await query.edit_message_text(
        texts.get(lang, texts['uz_latin']),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_weather_by_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shahar nomi bo'yicha ob-havo ko'rsatish"""
    query = update.callback_query
    await query.answer()

    shahar = query.data.replace('weather_city_', '')
    lang = context.user_data.get('language', 'uz_latin')

    loading = {
        'uz_latin': f"⏳ {shahar} ob-havosi olinmoqda...",
        'uz_kiril': f"⏳ {shahar} об-ҳавоси олинмоқда...",
        'en': f"⏳ Getting weather for {shahar}..."
    }.get(lang, f"⏳ {shahar} ob-havosi olinmoqda...")

    await query.edit_message_text(loading)

    result = await get_weather_by_city(shahar, WEATHER_API_KEY)

    if result["success"]:
        text = format_weather(result, lang)
    else:
        text = format_weather(result, lang)

    keyboard = [
        [InlineKeyboardButton("🔄 Qaytadan", callback_data="weather_city_menu")],
        [InlineKeyboardButton("🔙 Ortga", callback_data="weather")],
        [InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def handle_weather_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lokatsiya orqali ob-havo ko'rsatish"""
    try:
        location = update.message.location
        if not location:
            return

        lat = location.latitude
        lon = location.longitude

        lang = context.user_data.get('language', 'uz_latin')

        loading = {
            'uz_latin': "⏳ Joylashuvingiz bo'yicha ob-havo olinmoqda...",
            'uz_kiril': "⏳ Жойлашувингиз бўйича об-ҳаво олинмоқда...",
            'en': "⏳ Getting weather for your location..."
        }.get(lang, "⏳ Ob-havo olinmoqda...")

        msg = await update.message.reply_text(loading)

        result = await get_weather_by_location(lat, lon, WEATHER_API_KEY)

        await msg.delete()

        if result["success"]:
            text = format_weather(result, lang)
        else:
            text = format_weather(result, lang)

        keyboard = [
            [InlineKeyboardButton("🔄 Qaytadan", callback_data="weather_location")],
            [InlineKeyboardButton("🔙 Ortga", callback_data="weather")],
            [InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]
        ]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Lokatsiya ob-havo xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi")

    context.user_data['waiting_for_weather_location'] = False