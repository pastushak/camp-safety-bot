import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os
from datetime import datetime

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Завантажуємо змінні з .env
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

# Конфігурація
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

class CampSafetyBot:
    def __init__(self):
        self.user_states = {}  # Для відстеження стану користувачів
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Стартове повідомлення з головним меню"""
        user = update.effective_user
        
        welcome_text = f"""
🏕️ Привіт, {user.first_name}! 

Я бот твого "Безпечного табору" - твій помічник у створенні безпечного та дружнього середовища.

🛡️ Тут ти можеш:
• Дізнатися про булінг та як з ним боротися
• Отримати підтримку та поради
• Анонімно повідомити про проблему
• Знайти допомогу в складній ситуації

Обирай, що тебе цікавить 👇
"""
        
        keyboard = [
            [InlineKeyboardButton("📚 Що таке булінг?", callback_data="what_is_bullying")],
            [InlineKeyboardButton("🛡️ Що робити якщо цькують?", callback_data="what_to_do")],
            [InlineKeyboardButton("👀 Якщо ти свідок", callback_data="witness")],
            [InlineKeyboardButton("📝 Анонімне звернення", callback_data="anonymous_report")],
            [InlineKeyboardButton("🔴 SOS - Потрібна допомога!", callback_data="sos")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка натискань кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "what_is_bullying":
            await self.explain_bullying(query)
        elif query.data == "what_to_do":
            await self.what_to_do(query)
        elif query.data == "witness":
            await self.witness_advice(query)
        elif query.data == "anonymous_report":
            await self.start_anonymous_report(query)
        elif query.data == "sos":
            await self.sos_handler(query, context)  # Додали context
        elif query.data == "back_to_menu":
            await self.back_to_menu(query)

    async def explain_bullying(self, query):
        """Пояснення що таке булінг"""
        text = """
📖 <b>Що таке булінг?</b>

<b>Булінг</b> - це коли одну людину <b>систематично</b> (не один раз, а багато разів) <b>ображають, принижують, б'ють або виключають з колективу</b>. 

Це не жарт і не сварка - це <b>навмисна жорстокість</b>.

🔍 <b>Види булінгу:</b>

<b>1. Фізичний булінг</b>
• Систематично б'ють, штовхають
• Кидають речі, ламають особисті речі

<b>2. Психологічний булінг</b>
• Систематично насміхаються, обзивають
• Принижують, лякають, розпускають чутки

<b>3. Соціальний булінг</b>
• Не пускають в гру, не дають сісти за стіл
• Спеціально ігнорують або роблять "ізгоєм"

<b>4. Кібербулінг</b>
• Пишуть образи в чатах
• Публікують фото без дозволу
• Створюють образливі меми

🚫 <b>Це НЕ булінг, якщо:</b>
• Діти один раз посварилися - це конфлікт
• Хтось випадково щось сказав - це не навмисне

Але якщо образи повторюються і тобі постійно боляче - це булінг!
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад до меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def what_to_do(self, query):
        """Поради що робити якщо цькують"""
        text = """
🛡️ <b>Що робити, якщо тебе цькують?</b>

Якщо хтось тебе <b>постійно ображає, б'є, лякає або принижує</b> - це не твоя провина. І ти <b>не один/одна</b>.

✅ <b>Кроки, які ти можеш зробити:</b>

<b>1. Не мовчи</b>
🔸 Розкажи дорослому, якому довіряєш:
• Вихователю/виховательці
• Психологу табору
• Лікарю чи медсестрі
• Адміністрації табору

Це не "ябедничання", а <b>захист себе</b>.

<b>2. Не відповідай агресією</b>
🔸 Не бий, не кричи, не мстися
🔸 Краще сказати спокійно: "Зупинись. Мені це неприємно"

<b>3. Шукай підтримку</b>
🔸 Поговори з другом/подругою
🔸 Попроси, щоб хтось був поруч

<b>4. Напиши нам анонімно</b>
🔸 Натисни "Анонімне звернення"
🔸 Ми побачимо твоє повідомлення й допоможемо

<b>5. Пам'ятай: ти не винен/винна</b>
🔸 Кожен має право на повагу та безпеку!
"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Анонімне звернення", callback_data="anonymous_report")],
            [InlineKeyboardButton("🔙 Назад до меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def witness_advice(self, query):
        """Поради для свідків булінгу"""
        text = """
👀 <b>Що робити, якщо ти свідок булінгу?</b>

Якщо ти бачиш, як <b>когось ображають, принижують, виключають з гри</b> - не мовчи. Твоя підтримка може змінити все!

💬 <b>Чому важливо не бути осторонь:</b>
🔹 Булінг не припиняється сам по собі
🔹 Той, кого цькують, часто боїться щось сказати
🔹 Мовчання - це підтримка кривдника
🔹 Якщо хтось стане на захист - інші теж зможуть

✅ <b>Як допомогти безпечно:</b>

<b>1. Не смійся і не підтримуй кривдників</b>
Навіть просто сміх підбадьорює того, хто знущається.

<b>2. Підійди до того, кого цькують</b>
Скажи: "Я бачив, що сталося. Це неправильно. Ти не один/одна."

<b>3. Розкажи дорослому</b>
Повідом вихователя, психолога чи адміністрацію.
Ти не "ябеда" - ти допомагаєш зупинити жорстокість.

<b>4. Напиши анонімно</b>
"Я бачив булінг у групі №__. Ось що сталося..."

💚 <b>Твоя підтримка - це сила!</b>
"""
        
        keyboard = [
            [InlineKeyboardButton("📝 Повідомити анонімно", callback_data="anonymous_report")],
            [InlineKeyboardButton("🔙 Назад до меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def start_anonymous_report(self, query):
        """Початок анонімного звернення"""
        text = """
📝 <b>Анонімне звернення</b>

👋 Тут ти можеш написати про ситуацію, яка тебе турбує.
Ми не питаємо, як тебе звати. Це <b>анонімно</b>.

Ми прочитаємо й зробимо все, щоб допомогти.

📬 <b>Напиши:</b>
• Що сталося?
• Коли це відбувається?
• У якій групі?
• Будь-які деталі, які вважаєш важливими

Можеш також надіслати фото чи скріншот, якщо це допоможе.

✍️ <b>Просто напиши наступним повідомленням, що хочеш розповісти.</b>
"""
        
        # Встановлюємо стан користувача
        user_id = query.from_user.id
        self.user_states[user_id] = "waiting_for_report"
        
        keyboard = [[InlineKeyboardButton("❌ Скасувати", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def handle_anonymous_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка анонімного звернення"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states or self.user_states[user_id] != "waiting_for_report":
            return
        
        # Очищаємо стан
        del self.user_states[user_id]
        
        # Формуємо повідомлення для адміністраторів
        report_text = f"""
🚨 <b>АНОНІМНЕ ЗВЕРНЕННЯ</b>

📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M')}
👤 Від: Анонімний користувач
📝 Повідомлення:

{update.message.text}

---
⚠️ Потрібна увага адміністрації!
"""
        
        # Відправляємо в адмін-чат
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=report_text,
                parse_mode=ParseMode.HTML
            )
            
            # Якщо є фото/документи
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=update.message.photo[-1].file_id,
                    caption="📎 Фото до анонімного звернення"
                )
        except Exception as e:
            logger.error(f"Помилка відправки в адмін-чат: {e}")
        
        # Підтверджуємо користувачу
        confirmation_text = """
✅ <b>Дякуємо!</b>

Ми отримали твоє повідомлення. Тебе почули.

Дорослі, яким можна довіряти, допоможуть розібратися з ситуацією.

💚 Ти зробив/зробила правильно, що не мовчиш!
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Назад до меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            confirmation_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def sos_handler(self, query, context):
        """Обробка SOS-сигналу"""
        user_id = query.from_user.id
        
        # Відправляємо екстрене повідомлення адміністраторам
        sos_text = f"""
🔴 <b>SOS! ЕКСТРЕНЕ ЗВЕРНЕННЯ!</b>

📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M')}
👤 Від: Анонімний користувач
🚨 Потрібна термінова допомога!

⚠️ НЕГАЙНО ЗВЕРНІТЬ УВАГУ!
"""
        
        try:
            await context.bot.send_message(  # Виправлено: використовуємо context замість query
                chat_id=ADMIN_CHAT_ID,
                text=sos_text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Помилка відправки SOS: {e}")
        
        # Встановлюємо стан для детального опису
        self.user_states[user_id] = "waiting_for_sos_details"
        
        text = """
🔴 <b>SOS - Екстрена допомога</b>

🛑 Ми бачимо, що тобі страшно або потрібна термінова допомога.

Твій сигнал уже отримали дорослі!

Хочеш коротко написати, що сталося? Це допоможе швидше знайти тебе та допомогти.

Але якщо не можеш писати - не хвилюйся, дорослі вже шукають спосіб допомогти.

✍️ Якщо можеш - опиши ситуацію наступним повідомленням.
"""
        
        keyboard = [
            [InlineKeyboardButton("🚫 Не можу писати зараз", callback_data="sos_no_details")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def handle_sos_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка деталей SOS"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states or self.user_states[user_id] != "waiting_for_sos_details":
            return
        
        del self.user_states[user_id]
        
        # Відправляємо деталі адміністраторам
        details_text = f"""
🔴 <b>ДЕТАЛІ SOS-ЗВЕРНЕННЯ</b>

📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M')}
📝 Додаткова інформація:

{update.message.text}

⚠️ ТЕРМІНОВА ДОПОМОГА ПОТРІБНА!
"""
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=details_text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Помилка відправки деталей SOS: {e}")
        
        # Підтверджуємо
        await update.message.reply_text(
            "✅ Інформацію передано. Допомога вже йде до тебе!",
            parse_mode=ParseMode.HTML
        )

    async def back_to_menu(self, query):
        """Повернення до головного меню"""
        await self.start_menu(query)

    async def start_menu(self, query):
        """Головне меню (для callback query)"""
        welcome_text = """
🏕️ <b>Безпечний табір</b>

🛡️ Обирай, що тебе цікавить:
"""
        
        keyboard = [
            [InlineKeyboardButton("📚 Що таке булінг?", callback_data="what_is_bullying")],
            [InlineKeyboardButton("🛡️ Що робити якщо цькують?", callback_data="what_to_do")],
            [InlineKeyboardButton("👀 Якщо ти свідок", callback_data="witness")],
            [InlineKeyboardButton("📝 Анонімне звернення", callback_data="anonymous_report")],
            [InlineKeyboardButton("🔴 SOS - Потрібна допомога!", callback_data="sos")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка текстових повідомлень"""
        user_id = update.effective_user.id
        
        # Перевіряємо стан користувача
        if user_id in self.user_states:
            if self.user_states[user_id] == "waiting_for_report":
                await self.handle_anonymous_report(update, context)
            elif self.user_states[user_id] == "waiting_for_sos_details":
                await self.handle_sos_details(update, context)
        else:
            # Якщо користувач пише без команди
            await update.message.reply_text(
                "Привіт! Натисни /start щоб почати роботу з ботом 🤖"
            )

    async def get_chat_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Тимчасова функція для отримання Chat ID"""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = getattr(update.effective_chat, 'title', 'Приватний чат')
        
        await update.message.reply_text(
            f"📋 <b>Інформація про чат:</b>\n\n"
            f"🆔 Chat ID: <code>{chat_id}</code>\n"
            f"📁 Тип: {chat_type}\n"
            f"📝 Назва: {chat_title}\n\n"
            f"💡 Скопіюйте Chat ID для налаштування адмін-чату",
            parse_mode=ParseMode.HTML
        )

def main():
    """Запуск бота"""
    # Перевіряємо наявність токенів
    if not BOT_TOKEN:
        print("❌ Помилка: BOT_TOKEN не знайдено в .env файлі!")
        return
    
    if not ADMIN_CHAT_ID:
        print("⚠️ Попередження: ADMIN_CHAT_ID не налаштовано. Анонімні звернення не працюватимуть.")
    
    # Створюємо екземпляр бота
    bot = CampSafetyBot()
    
    # Створюємо додаток
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Додаємо обробники
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("chatinfo", bot.get_chat_info))  # Тимчасова команда
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_message))
    
    # Запускаємо бота
    print("🤖 Бот 'Безпечний табір' запущено!")
    print("Натисніть Ctrl+C для зупинки")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()