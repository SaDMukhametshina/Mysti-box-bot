import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Безопасное получение токена - используем правильное имя переменной
TOKEN = os.environ.get('TOKEN') or os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    # Более информативное сообщение об ошибке
    logging.error("❌ Токен бота не найден!")
    logging.error("ℹ️ Установите переменную окружения TOKEN в настройках Railway")
    logging.error("ℹ️ Текущие переменные окружения: " + str(list(os.environ.keys())))
    # Вместо выхода, используем демо-режим для тестирования
    TOKEN = "demo_mode"
    logging.warning("⚠️ Бот запущен в демо-режиме без реального токена")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("🚀 Mysti Box Bot запускается на Railway...")

# Меры безопасности
AUTHORIZED_USERS = set()
BLOCKED_USERS = set()

# Главное меню
main_keyboard = [
    ["❔ Что такое Mysti Box", "📦 Заказать бокс"],
    ["🌍 Ассортимент", "📞 Контакты"],
    ["✨ Акции и скидки", "🛫 Доставка"]
]
reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

# URL изображений
IMAGE_URLS = {
    "start": "https://t.me/mystiiiiiiiiiiiiiii/2",
    "about": "https://t.me/mystiiiiiiiiiiiiiii/10", 
    "order": "https://t.me/mystiiiiiiiiiiiiiii/9",
    "assortment": "https://t.me/mystiiiiiiiiiiiiiii/8",
    "contacts": "",
    "promo": "",
    "delivery": "https://t.me/mystiiiiiiiiiiiiiii/7"
}

# Тексты для бота
TEXTS = {
    "start": "🪐 Привет, {user_name}! Добро пожаловать в Mysti Box!\n\nМы собрали для вас самые вкусные снеки из США 🇺🇸, Кореи 🇰🇷, Японии 🇯🇵, Испании 🇪🇸, Германии 🇩🇪, Китая 🇨🇳 и многих других стран 🌏\n\nВыбери раздел:",
    
    "about": "🌍 <b>Mysti Box: Мир вкусов у вас на пороге!</b>✨\n\nПредставьте: вы открываете коробку, а внутри — целое путешествие. Хрустящие чипсы, которые обожают в Китае... Шоколадка, ради которой стоит лететь в США... Напиток, который пьют на пляжах Испании... ✨\n\nЭто не мечта, это <b>Mysti Box!</b>\n\nМы собрали для вас самые топовые и свежие снеки из США, Японии, Германии, Англии, Таиланда и многих других стран. Каждый бокс — это:\n\n• Новые впечатления: Наполнение всегда разное, но неизменно вкусное.\n• Гарантия качества: Только хиты и бестселлеры из каждой страны.\n• Эффект ВАУ: Идеальный подарок себе или другу, который точно запомнится.\n\n<b>Mysti Box — попробуй мир на вкус!</b>💜",
    
    "order_main": "<b>Mysti Box Premium - 3500₽</b>\n\n💌 Что входит:\n• 15-20 разных снеков из разных стран\n• Смесь сладких и солёных сюрпризов\n• Напиток из далёкой страны\n• Редкие и лимитированные вкусы\n• Всегда свежие продукты\n\nЭто не просто коробка — это вкусное путешествие, эмоции и праздник внутри!🎴\n\n<b>Выбери способ заказа:</b>",
    
    "order_confirmation": "🎴 Отлично! Оформляем твой <b>Mysti Box</b>!\n\nДля заказа напиши нам:\n📱 Instagram: mystibox.ru\n💬 Telegram: @mystibox1\n\nИ укажи:\n• Имя и фамилию\n• Адрес и способ доставки\n• Предпочтения (если есть)\n\nМенеджер свяжется с тобой в течение 15 минут! ⚡",
    
    "manager_contact": "<b>📞 Свяжись с нашим менеджером:</b>\n\n📱 Instagram: @mystibox.ru\n💬 Telegram: @mystibox1\n\n⚡ Отвечаем в течение 15 минут!",
    
    "assortment": "<b>🍫 Сладости и батончики:</b>\n• Pocky Strawberry — культовые японские палочки\n• Hershey's — легендарный белый шоколад\n• Reese's Peanut Butter — топ США с арахисовой пастой\n• KitKat Peanut Butter — редкий вкус КитКата\n• Несквик вафли — нежные молочные вафельки\n• Kinder Hippo — любимчик взрослых и детей\n\n<b>🍪 Печенье и снеки:</b>\n• Maltesers Cookie — тающее печенье\n• M&M's Cookie — печенье с драже\n• Вафельные роллы Snickers и Twix — хрустящая новинка\n\n<b>🍢 Жвачки и сладости:</b>\n• Hubba Bubba Cola — большая жвачка\n• Skittles Sour Squishy — мягкие кислые скитлс\n• Fini суфле — нежные маршмеллоу\n• Haribo шипучие червячки\n\n<b>🥠 Снеки и азиатские вкусы:</b>\n• Lay's 'Блины с луком' — необычный азиатский вкус\n• 'Плоды сметанного яблока' — новый тренд\n• Лапша Samyang Buldak Carbonara — легенда Кореи\n\n<b>🧋 Напитки:</b>\n• Японская Hata Kosen — газировка\n• Fanta Chucky — редкие лимитированные вкусы\n\nИ ещё десятки других сюрпризов!🎴",
    
    "contacts": "<b>📞 Наши контакты:</b>\n\n📱 Instagram: mystibox.ru\n💬 Telegram: @mystibox1\n 🎴Telegram channel: @mystiboxes\n\n⚡ Отвечаем быстро!",
    
    "promo": "📢 <b>Текущие акции:</b>\n\n• ПРИВЕДИ ДРУГА — скидка <b>300₽</b> вам обоим\n💌 Идеально как подарок, потому что:\n✔ дарит эмоции, удивление и эффект 'вау'\n✔ подходит для любого возраста и случая\n✔ можно подарить на праздник или просто порадовать\n✔ универсально — понравится всем!\n\nАкция временная, успей воспользоваться! 🏃🏻‍♀️",
    
    "delivery": "🛫 <b>Способы доставки:</b>\n\n• СДЭК — 3-5 дней по России\n• Почта России — 5-7 дней\n• Яндекс Доставка — 1-2 дня по Казани\n\n💵 Стоимость доставки рассчитывается индивидуально\n📦 Заказ формируется и отправляется в течение 24 часов после подтверждения!"
}

# 🔒 Функции безопасности
def is_user_blocked(user_id: int) -> bool:
    return user_id in BLOCKED_USERS

def log_security_event(user_id: int, username: str, action: str):
    logger.warning(f"🔒 Событие безопасности: user_id={user_id}, username={username}, action={action}")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    if is_user_blocked(user.id):
        log_security_event(user.id, user.username, "BLOCKED_USER_TRY_ACCESS")
        return
    
    logger.info(f"🎯 Пользователь {user.first_name} (ID: {user.id}) запустил бота")
    
    if IMAGE_URLS["start"]:
        await update.message.reply_photo(
            photo=IMAGE_URLS["start"],
            caption=TEXTS["start"].format(user_name=user.first_name),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            TEXTS["start"].format(user_name=user.first_name),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    
    if is_user_blocked(user.id):
        log_security_event(user.id, user.username, "BLOCKED_USER_TRY_SEND_MESSAGE")
        return
    
    logger.info(f"👤 Пользователь {user.first_name} (ID: {user.id}): {text}")
    
    if text == "❔ Что такое Mysti Box":
        if IMAGE_URLS["about"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["about"],
                caption=TEXTS["about"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["about"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif text == "📦 Заказать бокс":
        order_keyboard = [["🧧 Заказать за 3500₽", "📞 Связаться с менеджером"], ["↩️ Назад"]]
        order_markup = ReplyKeyboardMarkup(order_keyboard, resize_keyboard=True)
        
        if IMAGE_URLS["order"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["order"],
                caption=TEXTS["order_main"],
                reply_markup=order_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["order_main"],
                reply_markup=order_markup,
                parse_mode='HTML'
            )
    
    elif text == "🧧 Заказать за 3500₽":
        if IMAGE_URLS["order"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["order"],
                caption=TEXTS["order_confirmation"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["order_confirmation"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif text == "📞 Связаться с менеджером":
        if IMAGE_URLS["contacts"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["contacts"],
                caption=TEXTS["manager_contact"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["manager_contact"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif text == "🌍 Ассортимент":
        if IMAGE_URLS["assortment"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["assortment"],
                caption=TEXTS["assortment"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["assortment"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif text == "📞 Контакты":
        if IMAGE_URLS["contacts"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["contacts"],
                caption=TEXTS["contacts"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["contacts"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif text == "✨ Акции и скидки":
        if IMAGE_URLS["promo"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["promo"],
                caption=TEXTS["promo"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["promo"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif text == "🛫 Доставка":
        if IMAGE_URLS["delivery"]:
            await update.message.reply_photo(
                photo=IMAGE_URLS["delivery"],
                caption=TEXTS["delivery"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                TEXTS["delivery"],
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif text == "↩️ Назад":
        await update.message.reply_text(
            "Возвращаемся в главное меню:",
            reply_markup=reply_markup
        )
    
    else:
        log_security_event(user.id, user.username, f"UNKNOWN_COMMAND: {text}")
        await update.message.reply_text(
            "Не совсем понял тебя ☺️ Выбери один из разделов меню:",
            reply_markup=reply_markup
        )

# 🔒 Команды администратора
async def admin_block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_IDS = [123456789]  # Замени на реальные ID админов
    user = update.message.from_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    if context.args:
        try:
            user_id_to_block = int(context.args[0])
            BLOCKED_USERS.add(user_id_to_block)
            await update.message.reply_text(f"✅ Пользователь {user_id_to_block} заблокирован")
            logger.warning(f"🔒 Админ {user.id} заблокировал пользователя {user_id_to_block}")
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID пользователя")

async def admin_unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_IDS = [123456789]  # Замени на реальные ID админов
    user = update.message.from_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    if context.args:
        try:
            user_id_to_unblock = int(context.args[0])
            BLOCKED_USERS.discard(user_id_to_unblock)
            await update.message.reply_text(f"✅ Пользователь {user_id_to_unblock} разблокирован")
            logger.warning(f"🔒 Админ {user.id} разблокировал пользователя {user_id_to_unblock}")
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID пользователя")

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    user_info = ""
    
    if update and update.message:
        user = update.message.from_user
        user_info = f" пользователь {user.id} ({user.username})"
    
    logger.error(f"❌ Ошибка{user_info}: {error}", exc_info=True)

# Запуск бота
def main():
    try:
        # Проверяем токен перед запуском
        if TOKEN == "demo_mode":
            logger.warning("⚠️ Бот запущен в демо-режиме. Для работы с Telegram установите переменную TOKEN")
            print("📝 Для настройки бота:")
            print("1. Получите токен у @BotFather")
            print("2. В Railway добавьте переменную окружения TOKEN")
            print("3. Перезапустите приложение")
            return
        
        # Создаем приложение
        application = Application.builder().token(TOKEN).build()
        
        # Обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("block", admin_block_user))
        application.add_handler(CommandHandler("unblock", admin_unblock_user))
        application.add_handler(MessageHandler(filters.TEXT, handle_message))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        print("🎴 Безопасный бот Mysti Box запущен! Работает 24/7 на Railway!")
        print("🔒 Режим безопасности активирован")
        print(f"🤖 Токен: {TOKEN[:10]}...")  # Логируем только начало токена для безопасности
        
        # Запускаем бота
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка запуска бота: {e}")
        print(f"❌ Ошибка: {e}")
        print("💡 Проверьте:")
        print("1. Правильность токена в переменной окружения TOKEN")
        print("2. Наличие интернет-соединения")
        print("3. Корректность настроек в Railway")

if __name__ == "__main__":
    main()