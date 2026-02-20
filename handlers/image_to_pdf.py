from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from PIL import Image
import io
import logging
import os

logger = logging.getLogger(__name__)


async def pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rasm → PDF funksiyasini boshlash"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    texts = {
        'uz_latin': "📸 <b>Rasmni PDF ga aylantirish</b>\n\n"
                    "Menga rasm yuboring, men uni PDF ga o'giraman.\n\n"
                    "📌 Qabul qilinadigan formatlar: JPG, PNG, BMP, WEBP\n\n"
                    "👉 Rasm yuboring:",
        'uz_kiril': "📸 <b>Расмни PDF га айлантириш</b>\n\n"
                    "Менга расм юборинг, мен уни PDF га ўгираман.\n\n"
                    "📌 Қабул қилинадиган форматлар: JPG, PNG, BMP, WEBP\n\n"
                    "👉 Расм юборинг:",
        'en': "📸 <b>Image to PDF converter</b>\n\n"
              "Send me an image, I'll convert it to PDF.\n\n"
              "📌 Supported formats: JPG, PNG, BMP, WEBP\n\n"
              "👉 Send an image:"
    }

    keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]]

    # Holatni saqlash
    context.user_data['waiting_for_image'] = True

    await query.edit_message_text(
        texts.get(lang, texts['uz_latin']),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rasmni qabul qilish va PDF ga aylantirish"""
    try:
        lang = context.user_data.get('language', 'uz_latin')

        # Rasm bormi?
        if not update.message.photo and not update.message.document:
            await update.message.reply_text("❌ Iltimos, rasm yuboring!")
            return

        # "Ishlayapman..." xabari
        processing_texts = {
            'uz_latin': "🔄 Rasm qayta ishlanmoqda...",
            'uz_kiril': "🔄 Расм қайта ишланмоқда...",
            'en': "🔄 Processing image..."
        }
        processing_msg = await update.message.reply_text(
            processing_texts.get(lang, processing_texts['uz_latin'])
        )

        # Rasmni olish
        if update.message.photo:
            # Oddiy rasm (telegram compress qilgan)
            photo = update.message.photo[-1]  # Eng katta rasm
            file = await context.bot.get_file(photo.file_id)
        elif update.message.document:
            # Fayl sifatida yuborilgan rasm
            doc = update.message.document
            if not doc.mime_type or not doc.mime_type.startswith('image/'):
                await processing_msg.delete()
                error_texts = {
                    'uz_latin': "❌ Bu rasm formati emas! JPG, PNG, BMP yuboring.",
                    'uz_kiril': "❌ Бу расм формати эмас! JPG, PNG, BMP юборинг.",
                    'en': "❌ This is not an image! Send JPG, PNG, BMP."
                }
                await update.message.reply_text(error_texts.get(lang, error_texts['uz_latin']))
                return
            file = await context.bot.get_file(doc.file_id)
        else:
            await processing_msg.delete()
            await update.message.reply_text("❌ Rasm topilmadi!")
            return

        # Rasmni yuklab olish
        image_bytes = io.BytesIO()
        await file.download_to_memory(image_bytes)
        image_bytes.seek(0)

        try:
            # Rasmni ochish
            image = Image.open(image_bytes)

            # RGB formatiga o'tkazish (PDF uchun kerak)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Alpha kanalini o'chirish
                bg = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                bg.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = bg
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # PDF yaratish
            pdf_bytes = io.BytesIO()
            image.save(pdf_bytes, format='PDF', save_all=True)
            pdf_bytes.seek(0)

            # PDF nomi
            pdf_name = f"image_{update.message.from_user.id}.pdf"

            # "Ishlayapman..." xabarini o'chirish
            await processing_msg.delete()

            # PDF ni yuborish
            success_texts = {
                'uz_latin': "✅ PDF ga aylantirildi!",
                'uz_kiril': "✅ PDF га айлантирилди!",
                'en': "✅ Converted to PDF!"
            }

            await update.message.reply_document(
                document=pdf_bytes,
                filename=pdf_name,
                caption=success_texts.get(lang, success_texts['uz_latin'])
            )

            # Qayta foydalanish uchun
            again_texts = {
                'uz_latin': "📸 Yana rasm yuborishingiz mumkin (yoki /start bosing)",
                'uz_kiril': "📸 Яна расм юборишингиз мумкин (ёки /start босинг)",
                'en': "📸 You can send another image (or press /start)"
            }

            keyboard = [[InlineKeyboardButton("🏠 Asosiy menyu", callback_data="back_to_menu")]]

            await update.message.reply_text(
                again_texts.get(lang, again_texts['uz_latin']),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as img_error:
            logger.error(f"Rasmni ochishda xatolik: {img_error}")
            await processing_msg.delete()
            error_texts = {
                'uz_latin': "❌ Rasmni o'qib bo'lmadi. Boshqa rasm yuboring.",
                'uz_kiril': "❌ Расмни ўқиб бўлмади. Бошқа расм юборинг.",
                'en': "❌ Could not read image. Send another one."
            }
            await update.message.reply_text(error_texts.get(lang, error_texts['uz_latin']))
            return

    except Exception as e:
        logger.error(f"PDF yaratishda xatolik: {e}")
        error_texts = {
            'uz_latin': "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
            'uz_kiril': "❌ Хато юз берди. Қайтадан уриниб кўринг.",
            'en': "❌ An error occurred. Please try again."
        }
        await update.message.reply_text(error_texts.get(lang, error_texts['uz_latin']))

    # Holatni tozalash
    context.user_data['waiting_for_image'] = False