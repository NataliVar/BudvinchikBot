import logging
import re
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          ConversationHandler, ContextTypes, filters)

# Етапи анкети
(SELECT_ROLE, ENTER_CITY, ENTER_PHONE, ENTER_NAME, ENTER_PHOTO, ENTER_WORK_TYPES,
 ENTER_SEARCH_ROLE, ENTER_WORK_PHOTOS) = range(8)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Список міст України (при потребі доповнити)
CITIES = [
    "Київ", "Харків", "Одеса", "Дніпро", "Львів",
    "Запоріжжя", "Кривий Ріг", "Миколаїв", "Маріуполь", "Вінниця",
    "Херсон", "Чернігів", "Полтава", "Черкаси", "Суми",
    "Івано-Франківськ", "Тернопіль", "Ужгород", "Луцьк", "Рівне"
]
CITIES.sort()
CITIES.insert(0, "Київ")

# Види робіт
WORK_TYPES = ["Плитка", "Гіпсокартон", "Малярні роботи", "Електрика", "Комплексний ремонт"]
SEARCH_ROLES = ["Помічника", "Напарника", "Прораба"]
OFFER_ROLES = ["Помічник", "Напарник", "Прораб"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Знайти"], ["Запропонувати себе"]]
    await update.message.reply_text(
        "👋 Привіт! Що ти хочеш зробити?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return SELECT_ROLE

async def select_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    context.user_data['choice'] = choice

    if choice == "Знайти":
        await update.message.reply_text(
            "🔎 Вітаю тебе, майстре! Щоб знайти ідеального помічника, потрібно відповісти на декілька питань.\n\n📍 Обери місто, в якому здійснюєш пошук:",
            reply_markup=ReplyKeyboardMarkup([[city] for city in CITIES], resize_keyboard=True)
        )
    else:
        await update.message.reply_text(
            "🧰 Вітаю тебе, майстре! Щоб запропонувати себе, потрібно відповісти на декілька питань.\n\n📍 Обери місто, в якому здійснюєш пошук:",
            reply_markup=ReplyKeyboardMarkup([[city] for city in CITIES], resize_keyboard=True)
        )

    return ENTER_CITY

async def enter_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update.message.reply_text("📞 Введи свій номер телефону у форматі 0991234567:", reply_markup=ReplyKeyboardRemove())
    return ENTER_PHONE

async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not re.fullmatch(r"0\d{9}", phone):
        await update.message.reply_text("⚠️ Невірний формат. Введи номер у форматі: 0991234567")
        return ENTER_PHONE

    context.user_data['phone'] = phone
    await update.message.reply_text("👤 Введи ім’я, прізвище та вік (наприклад: Іван Петренко, 32):")
    return ENTER_NAME

async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📸 Завантаж своє фото:")
    return ENTER_PHOTO

async def enter_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    context.user_data['photo'] = photo_file

    if context.user_data['choice'] == "Знайти":
        await update.message.reply_text(
            "🔧 Які види робіт тебе цікавлять?",
            reply_markup=ReplyKeyboardMarkup([[wt] for wt in WORK_TYPES], resize_keyboard=True)
        )
        return ENTER_WORK_TYPES
    else:
        await update.message.reply_text(
            "🔧 Які види робіт ти пропонуєш?",
            reply_markup=ReplyKeyboardMarkup([[wt] for wt in WORK_TYPES], resize_keyboard=True)
        )
        return ENTER_WORK_TYPES

async def enter_work_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['work_types'] = update.message.text

    if context.user_data['choice'] == "Знайти":
        await update.message.reply_text(
            "👤 Кого ти шукаєш?",
            reply_markup=ReplyKeyboardMarkup([[r] for r in SEARCH_ROLES], resize_keyboard=True)
        )
        return ENTER_SEARCH_ROLE
    else:
        await update.message.reply_text("📸 Завантаж 2–5 фото своїх робіт:")
        context.user_data['work_photos'] = []
        return ENTER_WORK_PHOTOS

async def enter_search_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['search_role'] = update.message.text
    await update.message.reply_text("✅ Дякую! Ми почнемо пошук підходящих людей у твоєму місті.")
    return ConversationHandler.END

async def enter_work_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    context.user_data['work_photos'].append(photo_file)

    if len(context.user_data['work_photos']) >= 2:
        await update.message.reply_text("✅ Дякуємо! Твоя анкета надіслана. Очікуй на відгуки.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("📷 Завантаж ще фото своїх робіт (мінімум 2):")
        return ENTER_WORK_PHOTOS

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Дію скасовано.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    import os
    from telegram.ext import ApplicationBuilder

    TOKEN = "7948052574:AAGCJIIz6o5cXX8WlgXQPmusJJm1ZLcQvYI"  # 🔁 Встав сюди свій токен
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_role)],
            ENTER_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_city)],
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone)],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)],
            ENTER_PHOTO: [MessageHandler(filters.PHOTO, enter_photo)],
            ENTER_WORK_TYPES: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_work_types)],
            ENTER_SEARCH_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_search_role)],
            ENTER_WORK_PHOTOS: [MessageHandler(filters.PHOTO, enter_work_photos)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    print("🔧 Стартує бот...")
    app.run_polling()
    print("✅ Бот запущено. Очікує команди /start")
