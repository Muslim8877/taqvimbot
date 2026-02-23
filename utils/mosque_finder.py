import aiohttp
import logging
from math import radians, sin, cos, sqrt, atan2
from typing import List, Dict
import asyncio

logger = logging.getLogger(__name__)

# Qidiruv radiusi (metr)
QIDIRUV_RADIUSI = 3000  # 3 km


async def find_masjid(lat: float, lon: float) -> List[Dict]:
    """
    Joylashuvga eng yaqin masjidlarni topish
    """
    try:
        # Overpass API so'rovi
        overpass_url = "https://overpass-api.de/api/interpreter"

        query = f"""
        [out:json][timeout:5];
        (
          node["amenity"="place_of_worship"]["religion"="muslim"](around:{QIDIRUV_RADIUSI},{lat},{lon});
          way["amenity"="place_of_worship"]["religion"="muslim"](around:{QIDIRUV_RADIUSI},{lat},{lon});
        );
        out body;
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(overpass_url, params={"data": query}, timeout=5) as response:
                data = await response.json()

                elements = data.get("elements", [])
                masjidlar = []

                for element in elements[:15]:
                    element_lat = element.get("lat")
                    element_lon = element.get("lon")

                    if not element_lat and "center" in element:
                        element_lat = element["center"].get("lat")
                        element_lon = element["center"].get("lon")

                    if element_lat and element_lon:
                        distance = calculate_distance(lat, lon, element_lat, element_lon)

                        tags = element.get("tags", {})
                        name = tags.get("name", "🏢 Masjid")

                        address = ""
                        if "addr:street" in tags:
                            address += tags["addr:street"]
                        if "addr:housenumber" in tags:
                            address += " " + tags["addr:housenumber"]
                        if "addr:city" in tags:
                            address += f", {tags['addr:city']}" if address else tags["addr:city"]

                        masjidlar.append({
                            "name": name,
                            "lat": element_lat,
                            "lon": element_lon,
                            "distance": round(distance),
                            "address": address or "Manzil mavjud emas"
                        })

                masjidlar.sort(key=lambda x: x["distance"])
                return masjidlar[:5]

    except asyncio.TimeoutError:
        logger.warning("Overpass API timeout")
        return []
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        return []


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    lat1_rad, lat2_rad = radians(lat1), radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def format_masjid_list(masjidlar: List[Dict], lang: str = "uz_latin") -> str:
    """Masjidlar ro'yxatini formatlash (HTML)"""
    if not masjidlar:
        texts = {
            'uz_latin': "❌ Atrofingizda masjid topilmadi.",
            'uz_kiril': "❌ Атрофингизда масжид топилмади.",
            'en': "❌ No mosques found nearby."
        }
        return texts.get(lang, texts['uz_latin'])

    titles = {
        'uz_latin': "🕌 <b>Eng yaqin masjidlar:</b>\n\n",
        'uz_kiril': "🕌 <b>Энг яқин масжидлар:</b>\n\n",
        'en': "🕌 <b>Nearest mosques:</b>\n\n"
    }

    text = titles.get(lang, titles['uz_latin'])

    for i, m in enumerate(masjidlar, 1):
        if m['distance'] < 1000:
            masofa = f"{m['distance']} m"
        else:
            masofa = f"{round(m['distance'] / 1000, 2)} km"

        text += f"{i}. <b>{m['name']}</b>\n   📏 {masofa}\n"
        if m['address'] and m['address'] != "Manzil mavjud emas":
            text += f"   📍 {m['address']}\n"
        text += "\n"

    texts_end = {
        'uz_latin': "📍 Batafsil ma'lumot uchun masjid nomini bosing.",
        'uz_kiril': "📍 Батафсил маълумот учун масжид номини босинг.",
        'en': "📍 Click on a mosque name for details."
    }
    text += texts_end.get(lang, texts_end['uz_latin'])

    return text


def format_masjid_detail(masjid: Dict, lang: str = "uz_latin") -> str:
    """Bitta masjid haqida batafsil (HTML)"""
    if masjid['distance'] < 1000:
        masofa = f"{masjid['distance']} metr"
    else:
        masofa = f"{round(masjid['distance'] / 1000, 2)} km"

    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={masjid['lat']},{masjid['lon']}"

    texts = {
        'uz_latin': f"""
🏢 <b>{masjid['name']}</b>

📍 <b>Manzil:</b> {masjid['address']}
📏 <b>Masofa:</b> {masofa}

🗺 <a href="{maps_url}">Google Maps orqali yo'nalish</a>
""",
        'uz_kiril': f"""
🏢 <b>{masjid['name']}</b>

📍 <b>Манзил:</b> {masjid['address']}
📏 <b>Масофа:</b> {masofa}

🗺 <a href="{maps_url}">Google Maps орқали йўналиш</a>
""",
        'en': f"""
🏢 <b>{masjid['name']}</b>

📍 <b>Address:</b> {masjid['address']}
📏 <b>Distance:</b> {masofa}

🗺 <a href="{maps_url}">Get directions on Google Maps</a>
"""
    }

    return texts.get(lang, texts['uz_latin']).strip()