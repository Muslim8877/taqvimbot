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

SAHARLIK_DUO = {
    'uz_latin': "🤲 **Saharlik duosi:**\n\nNavaytu an asuma sovma shahri Ramazona minal fajri ilal mag'ribi, xolisan lillahi ta'ala. Allohu akbar.",
    'uz_kiril': "🤲 **Саҳарлик дуоси:**\n\nНавайту ан асума совма шаҳри Рамазона минал фажри илал мағриби, холисан лиллаҳи таъала. Аллоҳу акбар.",
    'en': "🤲 **Suhoor Dua:**\n\nI intend to keep the fast for tomorrow in the month of Ramadan, sincerely for Allah. Allahu Akbar."
}

IFTORLIK_DUO = {
    'uz_latin': "🤲 **Iftorlik duosi:**\n\nAllohumma laka sumtu va bika amantu va 'alayka tavakkaltu va 'ala rizqika aftartu, fag'firli ma qoddamtu va ma axxortu.",
    'uz_kiril': "🤲 **Ифторлик дуоси:**\n\nАллоҳумма лака сумту ва бика аманту ва ъалайка таваккалту ва ъала ризқика афтарту, фағфирли ма қоддамту ва ма аххорту.",
    'en': "🤲 **Iftar Dua:**\n\nO Allah, I fasted for You and I believe in You and I put my trust in You and I break my fast with Your sustenance. Forgive me my past and future sins."
}


async def get_roza_vaqtlari(viloyat: str):
    try:
        api_nom = API_VILOYATLAR.get(viloyat, "Tashkent")

        url = "http://api.aladhan.com/v1/timingsByCity"
        params = {
            "city": api_nom,
            "country": "Uzbekistan",
            "method": 2,
            "school": 1
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data["code"] == 200:
            timings = data["data"]["timings"]
            date = data["data"]["date"]["readable"]
            hijri = data["data"]["date"]["hijri"]
            weekday = data["data"]["date"]["hijri"]["weekday"]["en"]

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
                "saharlik": timings["Fajr"][:5],
                "iftorlik": timings["Maghrib"][:5]
            }
        return {"success": False}
    except:
        return {"success": False}


def format_roza_vaqtlari(data: dict, lang: str = "uz_latin"):
    if not data.get("success"):
        return "❌ Roza vaqtlarini olishda xatolik."

    texts = {
        'uz_latin': {
            'title': f"🌙 {data['viloyat']} roza vaqtlari",
            'sana': "📅 Sana",
            'hijriy': "📆 Hijriy",
            'saharlik': "🌅 Saharlik (og'iz yopish)",
            'iftorlik': "🌇 Iftorlik (og'iz ochish)",
            'sahar_duo': SAHARLIK_DUO['uz_latin'],
            'iftar_duo': IFTORLIK_DUO['uz_latin'],
            'footer': "⏱ Toshkent vaqti bilan",
            'aniqlik': "⚠️ +- 1 daqiqa aniqlikda"
        },
        'uz_kiril': {
            'title': f"🌙 {data['viloyat']} роза вақтлари",
            'sana': "📅 Сана",
            'hijriy': "📆 Ҳижрий",
            'saharlik': "🌅 Саҳарлик (оғиз ёпиш)",
            'iftorlik': "🌇 Ифторлик (оғиз очиш)",
            'sahar_duo': SAHARLIK_DUO['uz_kiril'],
            'iftar_duo': IFTORLIK_DUO['uz_kiril'],
            'footer': "⏱ Тошкент вақти билан",
            'aniqlik': "⚠️ +- 1 дақиқа аниқликда"
        },
        'en': {
            'title': f"🌙 {data['viloyat']} fasting times",
            'sana': "📅 Date",
            'hijriy': "📆 Hijri",
            'saharlik': "🌅 Suhoor (fast starts)",
            'iftorlik': "🌇 Iftar (fast breaks)",
            'sahar_duo': SAHARLIK_DUO['en'],
            'iftar_duo': IFTORLIK_DUO['en'],
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

{t['saharlik']}:  **{data['saharlik']}**
{t['iftorlik']}:  **{data['iftorlik']}**

{t['sahar_duo']}

{t['iftar_duo']}

{t['footer']}
{t['aniqlik']}
"""