import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Безопасное получение токена
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("❌ Токен бота не найден! Установите переменную окружения TELEGRAM_BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("🚀 Mysti Box Bot запускается на Railway...")

# Меры безопасности
AUTHORIZED_USERS = set()  # Можно добавить ID авторизованных пользователей
BLOCKED_USERS = set()     # Заблокированные пользователи

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
    
    "contacts": "<b>📞 Наши контакты:</b>\n\n📱 Instagram: mystibox.ru\n💬 Telegram: @mystibox1\n\n⚡ Отвечаем быстро!",
    
    "promo": "📢 <b>Текущие акции:</b>\n\n• ПРИВЕДИ ДРУГА — скидка <b>300₽</b> вам обоим\n💌 Идеально как подарок, потому что:\n✔ дарит эмоции, удивление и эффект 'вау'\n✔ подходит для любого возраста и случая\n✔ можно подарить на праздник или просто порадовать\n✔ универсально — понравится всем!\n\nАкция временная, успей воспользоваться! 🏃🏻‍♀️",
    
    "delivery": "🛫 <b>Способы доставки:</b>\n\n• СДЭК — 3-5 дней по России\n• Почта России — 5-7 дней\n• Яндекс Доставка — 1-2 дня по Казани\n\n💵 Стоимость доставки рассчитывается индивидуально\n📦 Заказ формируется и отправляется в течение 24 часов после подтверждения!"
}

# 🔒 Функции безопасности
def is_user_blocked(user_id: int) -> bool:
    """Проверка, заблокирован ли пользователь"""
    return user_id in BLOCKED_USERS

def log_security_event(user_id: int, username: str, action: str):
    """Логирование событий безопасности"""
    logger.warning(f"🔒 Событие безопасности: user_id={user_id}, username={username}, action={action}")

def safe_send_message(update: Update, text: str, photo_url: str = None, reply_markup=None):
    """Безопасная отправка сообщения с обработкой ошибок"""
    try:
        if photo_url:
            return update.message.reply_photo(
                photo=photo_url,
                caption=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            return update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        # Пытаемся отправить без фото в случае ошибки
        try:
            update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e2:
            logger.error(f"Критическая ошибка отправки: {e2}")

# Команда /start
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    
    # 🔒 Проверка безопасности
    if is_user_blocked(user.id):
        log_security_event(user.id, user.username, "BLOCKED_USER_TRY_ACCESS")
        return
    
    logger.info(f"🎯 Пользователь {user.first_name} (ID: {user.id}) запустил бота")
    
    safe_send_message(
        update,
        TEXTS["start"].format(user_name=user.first_name),
        IMAGE_URLS["start"],
        reply_markup
    )

# Обработка текстовых сообщений
def handle_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    text = update.message.text
    
    # 🔒 Проверка безопасности
    if is_user_blocked(user.id):
        log_security_event(user.id, user.username, "BLOCKED_USER_TRY_SEND_MESSAGE")
        return
    
    # Логируем действия пользователя
    logger.info(f"👤 Пользователь {user.first_name} (ID: {user.id}): {text}")
    
    if text == "❔ Что такое Mysti Box":
        safe_send_message(update, TEXTS["about"], IMAGE_URLS["about"], reply_markup)
    
    elif text == "📦 Заказать бокс":
        order_keyboard = [["🧧 Заказать за 3500₽", "📞 Связаться с менеджером"], ["↩️ Назад"]]
        order_markup = ReplyKeyboardMarkup(order_keyboard, resize_keyboard=True)
        safe_send_message(update, TEXTS["order_main"], IMAGE_URLS["order"], order_markup)
    
    elif text == "🧧 Заказать за 3500₽":
        safe_send_message(update, TEXTS["order_confirmation"], IMAGE_URLS["order"], reply_markup)
    
    elif text == "📞 Связаться с менеджером":
        safe_send_message(update, TEXTS["manager_contact"], IMAGE_URLS["contacts"], reply_markup)
    
    elif text == "🌍 Ассортимент":
        safe_send_message(update, TEXTS["assortment"], IMAGE_URLS["assortment"], reply_markup)
    
    elif text == "📞 Контакты":
        safe_send_message(update, TEXTS["contacts"], IMAGE_URLS["contacts"], reply_markup)
    
    elif text == "✨ Акции и скидки":
        safe_send_message(update, TEXTS["promo"], IMAGE_URLS["promo"], reply_markup)
    
    elif text == "🛫 Доставка":
        safe_send_message(update, TEXTS["delivery"], IMAGE_URLS["delivery"], reply_markup)
    
    elif text == "↩️ Назад":
        update.message.reply_text("Возвращаемся в главное меню:", reply_markup=reply_markup)
    
    else:
        # 🔒 Логируем неизвестные команды
        log_security_event(user.id, user.username, f"UNKNOWN_COMMAND: {text}")
        update.message.reply_text(
            "Не совсем понял тебя ☺️ Выбери один из разделов меню:",
            reply_markup=reply_markup
        )

# 🔒 Команды администратора для безопасности
def admin_block_user(update: Update, context: CallbackContext):
    """Команда для блокировки пользователя (только для админов)"""
    user = update.message.from_user
    
    # Проверяем, является ли пользователь администратором
    # Добавь свои ID администраторов
    ADMIN_IDS = [123456789]  # Замени на реальные ID админов
    
    if user.id not in ADMIN_IDS:
        update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    if context.args:
        try:
            user_id_to_block = int(context.args[0])
            BLOCKED_USERS.add(user_id_to_block)
            update.message.reply_text(f"✅ Пользователь {user_id_to_block} заблокирован")
            logger.warning(f"🔒 Админ {user.id} заблокировал пользователя {user_id_to_block}")
        except ValueError:
            update.message.reply_text("❌ Неверный формат ID пользователя")

def admin_unblock_user(update: Update, context: CallbackContext):
    """Команда для разблокировки пользователя (только для админов)"""
    user = update.message.from_user
    ADMIN_IDS = [123456789]  # Замени на реальные ID админов
    
    if user.id not in ADMIN_IDS:
        update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    if context.args:
        try:
            user_id_to_unblock = int(context.args[0])
            BLOCKED_USERS.discard(user_id_to_unblock)
            update.message.reply_text(f"✅ Пользователь {user_id_to_unblock} разблокирован")
            logger.warning(f"🔒 Админ {user.id} разблокировал пользователя {user_id_to_unblock}")
        except ValueError:
            update.message.reply_text("❌ Неверный формат ID пользователя")

# Обработка ошибок
def error_handler(update: Update, context: CallbackContext):
    """Обработчик ошибок с логированием"""
    error = context.error
    user_info = ""
    
    if update and update.message:
        user = update.message.from_user
        user_info = f" пользователь {user.id} ({user.username})"
    
    logger.error(f"❌ Ошибка{user_info}: {error}", exc_info=True)
    
    # Логируем серьезные ошибки как события безопасности
    if "Forbidden" in str(error):
        log_security_event(user.id if update and update.message else 0, 
                         user.username if update and update.message else "unknown", 
                         f"FORBIDDEN_ERROR: {error}")

# Запуск бота
def main():
    try:
        updater = Updater(TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Обработчики команд
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("block", admin_block_user))
        dispatcher.add_handler(CommandHandler("unblock", admin_unblock_user))
        dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
        
        # Обработчик ошибок
        dispatcher.add_error_handler(error_handler)
        
        print("🎴 Безопасный бот Mysti Box запущен! Работает 24/7 на Railway!")
        print("🔒 Режим безопасности активирован")
        
        # Запускаем бота
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    main()