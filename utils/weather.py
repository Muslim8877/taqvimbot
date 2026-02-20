import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# OpenWeatherMap API sozlamalari
# API_KEY ni .env faylidan olish kerak
# Ro'yxatdan o'tish: https://openweathermap.org/api

async def get_weather_by_city(shahar: str, api_key: str):
    """Shahar nomi bo'yicha ob-havo olish"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{shahar},UZ",
            "appid": api_key,
            "units": "metric",
            "lang": "uz"
        }

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("cod") == 200:
            return format_weather_data(data, shahar)
        else:
            return {"success": False, "error": "Shahar topilmadi"}

    except Exception as e:
        logger.error(f"Ob-havo xatolik: {e}")
        return {"success": False, "error": str(e)}


async def get_weather_by_location(lat: float, lon: float, api_key: str):
    """Lokatsiya (koordinatalar) bo'yicha ob-havo olish"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric",
            "lang": "uz"
        }

        logger.info(f"📍 Ob-havo so'rovi: lat={lat}, lon={lon}")

        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("cod") == 200:
            shahar = data.get("name", "Sizning joylashuvingiz")
            return format_weather_data(data, shahar)
        else:
            return {"success": False, "error": "Ob-havo ma'lumoti olinmadi"}

    except Exception as e:
        logger.error(f"Ob-havo xatolik: {e}")
        return {"success": False, "error": str(e)}


def format_weather_data(data: dict, location_name: str):
    """Ob-havo ma'lumotlarini formatlash"""
    try:
        return {
            "success": True,
            "shahar": location_name,
            "harorat": round(data["main"]["temp"]),
            "his": round(data["main"]["feels_like"]),
            "namlik": data["main"]["humidity"],
            "shamol": data["wind"]["speed"],
            "bosim": data["main"]["pressure"],
            "holat": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "quyosh_chiqish": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
            "quyosh_botish": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
        }
    except Exception as e:
        logger.error(f"Ma'lumotlarni formatlashda xatolik: {e}")
        return {"success": False, "error": "Ma'lumotlar formati noto'g'ri"}


def format_weather(data: dict, lang: str = "uz_latin"):
    """Ob-havo ma'lumotlarini chiroyli qilib ko'rsatish"""
    if not data.get("success"):
        texts = {
            'uz_latin': f"❌ Ob-havo ma'lumotlarini olishda xatolik: {data.get('error', '')}",
            'uz_kiril': f"❌ Об-ҳаво маълумотларини олишда хато: {data.get('error', '')}",
            'en': f"❌ Error getting weather data: {data.get('error', '')}"
        }
        return texts.get(lang, texts['uz_latin'])

    # Holat uchun emoji
    holat_emoji = {
        'clear': '☀️',
        'clouds': '☁️',
        'rain': '🌧️',
        'drizzle': '🌦️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️',
        'fog': '🌫️'
    }

    holat = data['holat'].lower()
    emoji = '🌤️'
    for key, value in holat_emoji.items():
        if key in holat:
            emoji = value
            break

    texts = {
        'uz_latin': {
            'title': f"🌤 {data['shahar']} ob-havo {emoji}",
            'harorat': "🌡 Harorat",
            'his': "🤔 His qilinadi",
            'namlik': "💧 Namlik",
            'shamol': "💨 Shamol",
            'bosim': "📊 Bosim",
            'quyosh': "☀️ Quyosh",
            'chiqish': "Chiqish",
            'botish': "Botish",
            'holat': "📋 Holat"
        },
        'uz_kiril': {
            'title': f"🌤 {data['shahar']} об-ҳаво {emoji}",
            'harorat': "🌡 Ҳарорат",
            'his': "🤔 Ҳис қилинади",
            'namlik': "💧 Намлик",
            'shamol': "💨 Шамол",
            'bosim': "📊 Босим",
            'quyosh': "☀️ Қуёш",
            'chiqish': "Чиқиш",
            'botish': "Ботиш",
            'holat': "📋 Ҳолат"
        },
        'en': {
            'title': f"🌤 {data['shahar']} weather {emoji}",
            'harorat': "🌡 Temperature",
            'his': "🤔 Feels like",
            'namlik': "💧 Humidity",
            'shamol': "💨 Wind",
            'bosim': "📊 Pressure",
            'quyosh': "☀️ Sun",
            'chiqish': "Rise",
            'botish': "Set",
            'holat': "📋 Condition"
        }
    }

    t = texts.get(lang, texts['uz_latin'])

    return f"""
{t['title']}
{t['holat']}: {data['holat'].title()} {emoji}
{t['harorat']}: {data['harorat']}°C
{t['his']}: {data['his']}°C
{t['namlik']}: {data['namlik']}%
{t['shamol']}: {data['shamol']} m/s
{t['bosim']}: {data['bosim']} hPa
{t['quyosh']} {t['chiqish']}: {data['quyosh_chiqish']}
{t['quyosh']} {t['botish']}: {data['quyosh_botish']}
"""