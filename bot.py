import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from config import BOT_TOKEN

# Handlerlar
from handlers.start import start, show_main_menu
from handlers.language import language_selector, set_language
from handlers.namoz import namoz_menu, show_namoz_vaqtlari
from handlers.iftar import iftar_menu, show_roza_vaqtlari
from handlers.mosque import mosque_start, handle_location, mosque_callback
from handlers.image_to_pdf import pdf_start, handle_image

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def button_handler(update, context):
    """Barcha tugmalar bosilganda ishlaydi"""
    query = update.callback_query
    await query.answer()

    data = query.data
    logger.info(f"🔘 Tugma bosildi: {data}")

    # Til tanlash
    if data.startswith('lang_'):
        await set_language(update, context)

    # Tilni o'zgartirish
    elif data == 'change_language':
        await language_selector(update, context)

    # Namoz vaqtlari
    elif data == 'namoz':
        await namoz_menu(update, context)
    elif data.startswith('viloyat_'):
        await show_namoz_vaqtlari(update, context)

    # Roza vaqtlari
    elif data == 'iftar':
        await iftar_menu(update, context)
    elif data.startswith('iftar_'):
        await show_roza_vaqtlari(update, context)

    # Masjid
    elif data == 'masjid':
        await mosque_start(update, context)
    elif data.startswith('mosque_') or data == 'mosque_back':
        await mosque_callback(update, context)

    # Rasm → PDF
    elif data == 'pdf':
        await pdf_start(update, context)

    # Asosiy menyuga qaytish
    elif data == 'back_to_menu':
        await show_main_menu(update, context)

    # Boshqa tugmalar
    else:
        lang = context.user_data.get('language', 'uz_latin')
        messages = {
            'uz_latin': f"✅ {data} tanlandi\n⏳ Bu funksiya tayyorlanmoqda...",
            'uz_kiril': f"✅ {data} танланди\n⏳ Бу функция тайёрланмоқда...",
            'en': f"✅ {data} selected\n⏳ This function is being prepared..."
        }
        await query.edit_message_text(messages.get(lang, messages['uz_latin']))


async def handle_message(update, context):
    """Oddiy xabarlarni boshqarish"""
    try:
        # Agar rasm kutilayotgan bo'lsa
        if context.user_data.get('waiting_for_image'):
            await handle_image(update, context)
            context.user_data['waiting_for_image'] = False
            return

        # Agar lokatsiya kutilayotgan bo'lsa
        if context.user_data.get('waiting_for_location'):
            await handle_location(update, context)
            context.user_data['waiting_for_location'] = False
            return

        # Oddiy xabar
        lang = context.user_data.get('language', 'uz_latin')
        texts = {
            'uz_latin': "Iltimos, quyidagi tugmalardan birini tanlang:",
            'uz_kiril': "Илтимос, қуйидаги тугмалардан бирини танланг:",
            'en': "Please choose one of the buttons below:"
        }
        await update.message.reply_text(texts.get(lang, texts['uz_latin']))

    except Exception as e:
        logger.error(f"❌ Xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")


async def handle_photo(update, context):
    """Rasm xabarlarini boshqarish"""
    try:
        logger.info("📸 Rasm qabul qilindi")

        # Agar rasm kutilayotgan bo'lsa
        if context.user_data.get('waiting_for_image'):
            await handle_image(update, context)
            context.user_data['waiting_for_image'] = False
        else:
            # Rasm kutilmagan bo'lsa
            lang = context.user_data.get('language', 'uz_latin')
            texts = {
                'uz_latin': "📸 Rasm → PDF funksiyasidan foydalanish uchun menyudan tanlang!",
                'uz_kiril': "📸 Расм → PDF функсиясидан фойдаланиш учун менюдан танланг!",
                'en': "📸 To convert image to PDF, select from menu!"
            }
            await update.message.reply_text(texts.get(lang, texts['uz_latin']))

    except Exception as e:
        logger.error(f"❌ Rasm xatolik: {e}")


async def handle_location_message(update, context):
    """Lokatsiya xabarlarini boshqarish"""
    try:
        logger.info("📍 Lokatsiya qabul qilindi")

        # Agar lokatsiya kutilayotgan bo'lsa
        if context.user_data.get('waiting_for_location'):
            await handle_location(update, context)
            context.user_data['waiting_for_location'] = False
        else:
            # Lokatsiya kutilmagan bo'lsa
            lang = context.user_data.get('language', 'uz_latin')
            texts = {
                'uz_latin': "📍 Masjid qidirish funksiyasidan foydalanish uchun menyudan tanlang!",
                'uz_kiril': "📍 Масжид қидириш функсиясидан фойдаланиш учун менюдан танланг!",
                'en': "📍 To find nearby mosques, select from menu!"
            }
            await update.message.reply_text(texts.get(lang, texts['uz_latin']))

    except Exception as e:
        logger.error(f"❌ Lokatsiya xatolik: {e}")


async def error_handler(update, context):
    """Xatoliklarni boshqarish"""
    logger.error(f"❌ Update {update} caused error {context.error}")


def main():
    """Botni ishga tushirish"""
    print("=" * 60)
    print("🤖 TAQVIM BOT ISHGA TUSHMOQDA...")
    print("=" * 60)

    try:
        # Botni yaratish
        app = Application.builder().token(BOT_TOKEN).build()

        # Handlerlarni qo'shish
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        app.add_handler(MessageHandler(filters.LOCATION, handle_location_message))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Error handler
        app.add_error_handler(error_handler)

        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        print("=" * 60)
        print("📌 Faol funksiyalar:")
        print("   • 🕌 Namoz vaqtlari (13 viloyat)")
        print("   • 🌙 Roza vaqtlari (Saharlik + Iftorlik)")
        print("   • 📍 Eng yaqin masjid (lokatsiya bilan)")
        print("   • 📸 Rasm → PDF (JPG, PNG, BMP)")
        print("   • 🌐 3 xil til")
        print("=" * 60)
        print("⏳ Bot ishlamoqda...")
        print("=" * 60)

        # Pollingni boshlash
        app.run_polling()

    except Exception as e:
        print(f"❌ Xatolik: {e}")
        logger.error(f"Bot ishga tushmadi: {e}")


if __name__ == "__main__":
    main()