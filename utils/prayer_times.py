import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

VILOYATLAR = [
    "Toshkent", "Samarqand", "Buxoro", "Xiva", "Qarshi",
    "Namangan", "Andijon", "Farg'ona", "Jizzax", "Guliston",
    "Navoiy", "Urganch", "Termiz", "Nukus"
]

API_VILOYATLAR = {
    "Toshkent": "Tashkent",
    "Samarqand": "Samarkand",
    "Buxoro": "Bukhara",
    "Xiva": "Khiva",
    "Qarshi": "Karshi",
    "Namangan": "Namangan",
    "Andijon": "Andijan",
    "Farg'ona": "Fergana",
    "Jizzax": "Jizzakh",
    "Guliston": "Gulistan",
    "Navoiy": "Navoi",
    "Urganch": "Urgench",
    "Termiz": "Termez",
    "Nukus": "Nukus"
}


async def get_namoz_vaqtlari(viloyat: str):
    """Namoz vaqtlarini Aladhan API dan olish"""
    try:
        api_nom = API_VILOYATLAR.get(viloyat, "Tashkent")

        url = "http://api.aladhan.com/v1/timingsByCity"
        params = {
            "city": api_nom,
            "country": "Uzbekistan",
            "method": 2,  # Muslim World League
            "school": 1  # Hanafi
        }

        logger.info(f"API so'rov: {url}?city={api_nom}")

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data["code"] == 200:
            timings = data["data"]["timings"]
            date = data["data"]["date"]["readable"]
            hijri = data["data"]["date"]["hijri"]
            weekday = data["data"]["date"]["hijri"]["weekday"]["en"]

            # Hafta kunini o'zbekchalashtirish
            weekdays = {
                'Monday': 'Dushanba', 'Tuesday': 'Seshanba', 'Wednesday': 'Chorshanba',
                'Thursday': 'Payshanba', 'Friday': 'Juma', 'Saturday': 'Shanba', 'Sunday': 'Yakshanba'
            }
            weekday_uz = weekdays.get(weekday, weekday)

            return {
                "success": True,
                "viloyat": viloyat,
                "sana": date,
                "hafta_kuni": weekday_uz,
                "hijriy": f"{hijri['day']} {hijri['month']['en']} {hijri['year']}",
                "bomdod": timings["Fajr"][:5],
                "quyosh": timings["Sunrise"][:5],
                "peshin": timings["Dhuhr"][:5],
                "asr": timings["Asr"][:5],
                "shom": timings["Maghrib"][:5],
                "xufton": timings["Isha"][:5]
            }
        else:
            logger.error(f"API xatolik: {data}")
            return {"success": False}

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        return {"success": False}


def format_namoz_vaqtlari(data: dict, lang: str = "uz_latin"):
    """Namoz vaqtlarini chiroyli qilib ko'rsatish"""
    if not data.get("success"):
        return "❌ Namoz vaqtlarini olishda xatolik."

    texts = {
        'uz_latin': {
            'title': f"🕌 {data['viloyat']} namoz vaqtlari",
            'sana': "📅 Sana",
            'hijriy': "📆 Hijriy",
            'bomdod': "🌅 Bomdod",
            'quyosh': "☀️ Quyosh",
            'peshin': "🌤 Peshin",
            'asr': "🌥 Asr",
            'shom': "🌇 Shom",
            'xufton': "🌃 Xufton",
            'footer': "⏱ Toshkent vaqti bilan",
            'aniqlik': "⚠️ +- 1 daqiqa aniqlikda"
        },
        'uz_kiril': {
            'title': f"🕌 {data['viloyat']} намоз вақтлари",
            'sana': "📅 Сана",
            'hijriy': "📆 Ҳижрий",
            'bomdod': "🌅 Бомдод",
            'quyosh': "☀️ Қуёш",
            'peshin': "🌤 Пешин",
            'asr': "🌥 Аср",
            'shom': "🌇 Шом",
            'xufton': "🌃 Хуфтон",
            'footer': "⏱ Тошкент вақти билан",
            'aniqlik': "⚠️ +- 1 дақиқа аниқликда"
        },
        'en': {
            'title': f"🕌 {data['viloyat']} prayer times",
            'sana': "📅 Date",
            'hijriy': "📆 Hijri",
            'bomdod': "🌅 Fajr",
            'quyosh': "☀️ Sunrise",
            'peshin': "🌤 Dhuhr",
            'asr': "🌥 Asr",
            'shom': "🌇 Maghrib",
            'xufton': "🌃 Isha",
            'footer': "⏱ Tashkent time",
            'aniqlik': "⚠️ +- 1 minute accuracy"
        }
    }

    t = texts.get(lang, texts['uz_latin'])
    week = f", {data['hafta_kuni']}" if data['hafta_kuni'] else ""

    return f"""
{t['title']}{week}
{t['sana']}: {data['sana']}
{t['hijriy']}: {data['hijriy']}

{t['bomdod']}:  **{data['bomdod']}**
{t['quyosh']}:  **{data['quyosh']}**
{t['peshin']}:  **{data['peshin']}**
{t['asr']}:     **{data['asr']}**
{t['shom']}:    **{data['shom']}**
{t['xufton']}:  **{data['xufton']}**

{t['footer']}
{t['aniqlik']}
"""