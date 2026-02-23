from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


async def pdf_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rasm → PDF funksiyasini boshlash"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('language', 'uz_latin')

    texts = {
        'uz_latin': "📸 **Rasmni PDF ga aylantirish**\n\n"
                    "Menga rasm yuboring, men uni PDF ga o‘giraman.\n\n"
                    "Qabul qilinadigan formatlar: JPG, PNG, BMP",
        'uz_kiril': "📸 **Расмни PDF га айлантириш**\n\n"
                    "Менга расм юборинг, мен уни PDF га ўгираман.\n\n"
                    "Қабул қилинадиган форматлар: JPG, PNG, BMP",
        'en': "📸 **Image to PDF converter**\n\n"
              "Send me an image, I'll convert it to PDF.\n\n"
              "Supported formats: JPG, PNG, BMP"
    }

    keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]]

    context.user_data['waiting_for_image'] = True

    await query.edit_message_text(
        texts.get(lang, texts['uz_latin']),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rasmni qabul qilish va PDF ga aylantirish"""
    try:
        lang = context.user_data.get('language', 'uz_latin')

        # "Ishlayapman..." xabari
        processing = {
            'uz_latin': "⏳ Rasm qayta ishlanmoqda...",
            'uz_kiril': "⏳ Расм қайта ишланмоқда...",
            'en': "⏳ Processing image..."
        }
        msg = await update.message.reply_text(processing.get(lang, processing['uz_latin']))

        # Rasmni olish
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
        else:
            await msg.delete()
            await update.message.reply_text("❌ Rasm yuboring!")
            return

        # Rasmni yuklab olish
        image_bytes = io.BytesIO()
        await file.download_to_memory(image_bytes)
        image_bytes.seek(0)

        # PDF ga aylantirish
        image = Image.open(image_bytes)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        pdf_bytes = io.BytesIO()
        image.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)

        # PDF nomi
        pdf_name = f"rasm_{update.message.from_user.id}.pdf"

        # "Ishlayapman..." xabarini o'chirish
        await msg.delete()

        # PDF ni yuborish
        success = {
            'uz_latin': "✅ PDF ga aylantirildi!",
            'uz_kiril': "✅ PDF га айлантирилди!",
            'en': "✅ Converted to PDF!"
        }

        await update.message.reply_document(
            document=pdf_bytes,
            filename=pdf_name,
            caption=success.get(lang, success['uz_latin'])
        )

        # Yana rasm so'rash
        again = {
            'uz_latin': "📸 Yana rasm yuborishingiz mumkin:",
            'uz_kiril': "📸 Яна расм юборишингиз мумкин:",
            'en': "📸 You can send another image:"
        }

        keyboard = [[InlineKeyboardButton("🔙 Asosiy menyu", callback_data="back_to_menu")]]
        await update.message.reply_text(
            again.get(lang, again['uz_latin']),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"PDF xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi.")

    context.user_data['waiting_for_image'] = False