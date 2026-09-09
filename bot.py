import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ============================================================
# БОТ ДЛЯ MARKETING EVANGELIST
# ============================================================

BOT_TOKEN = "8834854950:AAEnPiiIz9a8GhF9V5CuUxM6638AFXNPhL0"
CHANNEL_URL = "https://t.me/leaderonthecouch"

# ============================================================
# СООБЩЕНИЯ ДЛЯ ФОРМЫ ЗАЯВКИ (?start=zayavka)
# ============================================================

ZAYAVKA_FIRST_TEXT = (
    "Ваша заявка принята. Скоро с вами свяжется наш менеджер "
    "для уточнения деталей.\n\n"
    "А пока подписывайтесь на наш канал — там много полезного "
    "о нейромаркетинге!"
)
ZAYAVKA_FIRST_IMAGE = "https://picsum.photos/800/600"  # Тестовая картинка

ZAYAVKA_SECOND_TEXT = (
    "👋 Напоминаем, что ваша заявка принята!\n\n"
    "Если у вас есть вопросы — наш менеджер скоро выйдет на связь.\n\n"
    "А пока загляните в наш канал — там много полезного о нейромаркетинге!"
)
ZAYAVKA_SECOND_IMAGE = None          # None = только текст, без картинки
ZAYAVKA_DELAY_MINUTES = 5            # Через сколько минут второе сообщение

# ============================================================
# СООБЩЕНИЯ ДЛЯ ФОРМЫ ОПЛАТЫ (?start=oplata)
# ============================================================

OPLATA_FIRST_TEXT = (
    "Поздравляем! 🎉\n\n"
    "Вы успешно зарегистрированы на программу прикладного "
    "нейромаркетинга «Бизнес по науке».\n\n"
    "В ближайшее время мы отправим вам доступ к материалам "
    "и расписание занятий.\n\n"
    "Подписывайтесь на наш канал, чтобы не пропустить важные обновления!"
)
OPLATA_FIRST_IMAGE = "https://picsum.photos/800/600"

OPLATA_SECOND_TEXT = (
    "🎓 Добро пожаловать в программу «Бизнес по науке»!\n\n"
    "В течение часа вы получите письмо с доступом к материалам.\n\n"
    "А пока рекомендуем подготовиться:\n"
    "✅ Проверьте, что у вас установлен Zoom\n"
    "✅ Подготовьте блокнот для заметок\n"
    "✅ Изучите программу курса в нашем канале"
)
OPLATA_SECOND_IMAGE = None           # None = только текст, без картинки
OPLATA_DELAY_MINUTES = 10            # Через сколько минут второе сообщение

# ============================================================
# КОД БОТА — НИЧЕГО НИЖЕ МЕНЯТЬ НЕ НУЖНО
# ============================================================

MESSAGES = {
    "zayavka": {
        "first":  {"text": ZAYAVKA_FIRST_TEXT,  "image": ZAYAVKA_FIRST_IMAGE},
        "second": {"text": ZAYAVKA_SECOND_TEXT, "image": ZAYAVKA_SECOND_IMAGE,
                   "delay": ZAYAVKA_DELAY_MINUTES},
    },
    "oplata": {
        "first":  {"text": OPLATA_FIRST_TEXT,  "image": OPLATA_FIRST_IMAGE},
        "second": {"text": OPLATA_SECOND_TEXT, "image": OPLATA_SECOND_IMAGE,
                   "delay": OPLATA_DELAY_MINUTES},
    },
}


async def send_message(bot, chat_id: int, text: str, image: str | None,
                       reply_markup):
    """Отправляет сообщение — с картинкой или только текст."""
    if image:
        await bot.send_photo(chat_id=chat_id, photo=image,
                             caption=text, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id=chat_id, text=text,
                               reply_markup=reply_markup)


async def send_delayed(chat_id: int, form_type: str,
                       context: ContextTypes.DEFAULT_TYPE):
    """Ждёт нужное время и отправляет второе сообщение."""
    data = MESSAGES.get(form_type, MESSAGES["zayavka"])["second"]
    await asyncio.sleep(data["delay"] * 60)

    keyboard = [[InlineKeyboardButton("📢 Подписаться на канал",
                                      url=CHANNEL_URL)]]
    await send_message(context.bot, chat_id,
                       data["text"], data["image"],
                       InlineKeyboardMarkup(keyboard))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик /start — вызывается когда пользователь открывает бота."""
    chat_id = update.effective_chat.id

    # Определяем тип формы из параметра ссылки (?start=zayavka / oplata)
    args = context.args
    form_type = args[0] if args and args[0] in MESSAGES else "zayavka"

    # Кнопка «Подписаться на канал»
    keyboard = [[InlineKeyboardButton("Подписаться на канал",
                                      url=CHANNEL_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Первое сообщение — сразу
    first = MESSAGES[form_type]["first"]
    await send_message(context.bot, chat_id,
                       first["text"], first["image"], reply_markup)

    # Второе сообщение — через N минут (в фоне, не блокирует бота)
    asyncio.create_task(send_delayed(chat_id, form_type, context))


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
