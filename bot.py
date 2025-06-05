import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os
from datetime import datetime

# Налаштування логування для продакшн
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Завантажуємо змінні з .env (локально) або з середовища (продакшн)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # В продакшн dotenv може не бути встановлено

logger = logging.getLogger(__name__)

# Конфігурація - читаємо з змінних середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
PORT = int(os.getenv("PORT", 8443))  # Для деяких хостингів

class CampSafetyBot:
    def __init__(self):
        self.user_states = {}  # Для відстеження стану користувачів
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Стартове повідомлення з головним меню"""
        user = update.effective_user
        
        welcome_text = f"""
🏕️ Привіт, {user.first_name}! 

Я бот "Безпечний табір" - твій помічник у створенні безпечного та дружнього середовища.

🛡️ Тут ти можеш:
• дізнатися про булінг та як з ним боротися;
• отримати підтримку та поради;
• анонімно повідомити про проблему;
• знайти допомогу в складній ситуації.

Обирай, що тебе цікавить 👇
"""
        
        keyboard = [
            [InlineKeyboardButton("📚 Що таке булінг?", callback_data="what_is_bullying")],
            [InlineKeyboardButton("🛡️ Що робити якщо цькують?", callback_data="what_to_do")],
            [InlineKeyboardButton("👀 Якщо ти свідок", callback_data="witness")],
            [InlineKeyboardButton("🆘 SOS - Анонімна допомога", callback_data="sos_help")]
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
        elif query.data == "sos_help":
            await self.sos_help_menu(query)
        elif query.data == "tell_story":
            await self.tell_story(query)
        elif query.data.startswith("gender_"):
            gender = query.data.replace("gender_", "")
            await self.ask_group(query, gender)
        elif query.data.startswith("group_"):
            group = query.data.replace("group_", "")
            await self.start_story_input(query, group)
        elif query.data == "back_to_menu":
            await self.back_to_menu(query)
        elif query.data == "back_to_sos":
            await self.sos_help_menu(query)

    async def explain_bullying(self, query):
        """Пояснення що таке булінг"""
        text = """
📖 <b>Що таке булінг?</b>

<b>Булінг</b> - це коли одну людину <b>систематично</b> (не один раз, а багато разів) <b>ображають, принижують, б'ють або виключають з колективу</b>. 

Це не жарт і не сварка - це <b>навмисна жорстокість</b>.

🔍 <b>Види булінгу:</b>

<b>1. Фізичний булінг</b>
• систематично б'ють, штовхають
• кидають речі, ламають особисті речі

<b>2. Психологічний булінг</b>
• систематично насміхаються, обзивають
• принижують, лякають, розпускають чутки

<b>3. Соціальний булінг</b>
• не пускають в гру, не дають сісти за стіл
• спеціально ігнорують або роблять "ізгоєм"

<b>4. Кібербулінг</b>
• пишуть образи в чатах
• публікують фото без дозволу
• створюють образливі меми

🚫 <b>Це НЕ булінг, якщо:</b>
• діти один раз посварилися - це конфлікт
• хтось випадково щось сказав - це не навмисне

Але якщо образи повторюються і тобі постійно боляче - це БУЛІНГ!
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
    • вихователю/виховательці
    • психологу табору
    • лікарю чи медсестрі
    • адміністрації табору

Це не "зведення наклепу", а <b>власний захист</b>.

<b>2. Не відповідай агресією</b>
🔸 Не бий, не кричи, не мстися
🔸 Краще сказати спокійно: "Зупинись. Мені це неприємно"

<b>3. Шукай підтримку</b>
🔸 Поговори з другом/подругою
🔸 Попроси, щоб хтось був поруч

<b>4. Звернись за допомогою анонімно</b>
🔸 Використай розділ "SOS - Допомога анонімно"
🔸 Ми побачимо твоє повідомлення й допоможемо

<b>5. Пам'ятай: ти не винен/винна</b>
🔸 Кожен має право на повагу та безпеку!
"""
        
        keyboard = [
            [InlineKeyboardButton("🆘 SOS - Анонімна допомога", callback_data="sos_help")],
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

<b>4. Повідом анонімно</b>
"Я бачив булінг у групі №__. Ось що сталося..."

💚 <b>Твоя підтримка - це сила!</b>
"""
        
        keyboard = [
            [InlineKeyboardButton("🆘 Повідомити анонімно", callback_data="sos_help")],
            [InlineKeyboardButton("🔙 Назад до меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def sos_help_menu(self, query):
        """Меню SOS - Допомога анонімно"""
        text = """
🆘 <b>SOS - Допомога анонімно</b>

👋 Тут ти можеш безпечно розповісти про будь-яку ситуацію, яка тебе турбує.
Ми не питаємо, як тебе звати. Це <b>повністю анонімно</b>.

📝 Розкажи:
• ЩО сталося?
• що ТЕБЕ турбує?
• потрібна допомога чи просто хочеш поділитися?

Ми прочитаємо і допоможемо!

✍️ <b>Натисни кнопку і розкажи свою історію.</b>
"""

        keyboard = [
            [InlineKeyboardButton("📝 Розповісти про ситуацію", callback_data="tell_story")],
            [InlineKeyboardButton("🔙 Назад до меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def tell_story(self, query):
        """Початок розповіді - збір базової інформації"""
        text = """
📝 <b>Розповісти про ситуацію</b>

Перш ніж ти розкажеш свою історію, допоможи нам краще зрозуміти контекст:

👤 <b>Твоя стать:</b>
"""
        
        keyboard = [
            [InlineKeyboardButton("👦 Хлопець", callback_data="gender_male")],
            [InlineKeyboardButton("👧 Дівчина", callback_data="gender_female")],
            [InlineKeyboardButton("🤐 Не хочу вказувати", callback_data="gender_skip")],
            [InlineKeyboardButton("🔙 Назад", callback_data="sos_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def ask_group(self, query, gender):
        """Питання про групу"""
        # Зберігаємо стать користувача
        user_id = query.from_user.id
        if user_id not in self.user_states:
            self.user_states[user_id] = {}
        
        # Перетворюємо технічні назви на читабельні
        gender_display = {
            'male': '👦 Хлопець',
            'female': '👧 Дівчина', 
            'skip': '🤐 Не вказано'
        }.get(gender, gender)
        
        self.user_states[user_id]['gender'] = gender_display
        
        text = """
🏕️ <b>У якій ти групі?</b>

Це допоможе нам швидше надати допомогу:
"""
        
        keyboard = [
            [InlineKeyboardButton("1️⃣ Група 1", callback_data="group_1")],
            [InlineKeyboardButton("2️⃣ Група 2", callback_data="group_2")],
            [InlineKeyboardButton("3️⃣ Група 3", callback_data="group_3")],
            [InlineKeyboardButton("4️⃣ Група 4", callback_data="group_4")],
            [InlineKeyboardButton("5️⃣ Група 5", callback_data="group_5")],
            [InlineKeyboardButton("🤐 Не хочу вказувати", callback_data="group_skip")],
            [InlineKeyboardButton("🔙 Назад", callback_data="tell_story")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

    async def start_story_input(self, query, group):
        """Початок введення тексту"""
        user_id = query.from_user.id
        if user_id not in self.user_states:
            self.user_states[user_id] = {}
        
        # Перетворюємо технічні назви на читабельні
        group_display = {
            '1': '1️⃣ Група 1',
            '2': '2️⃣ Група 2',
            '3': '3️⃣ Група 3', 
            '4': '4️⃣ Група 4',
            '5': '5️⃣ Група 5',
            'skip': '🤐 Не вказано'
        }.get(group, group)
        
        self.user_states[user_id]['group'] = group_display
        self.user_states[user_id]['status'] = "waiting_for_story"
        
        # Показуємо зібрану інформацію
        gender = self.user_states[user_id].get('gender', '🤐 Не вказано')
        
        text = f"""
✍️ <b>Тепер розкажи свою історію</b>

📋 <b>Інформація:</b>
👤 Стать: {gender}
🏕️ Група: {group_display}

📝 <b>Розкажи детально:</b>
• Що сталося?
• Коли це відбувається?
• Хто задіяний?
• Як довго це триває?
• Будь-які інші важливі деталі

Можеш також надіслати фото чи скріншот.

✍️ <b>Напиши наступним повідомленням свою історію.</b>
"""
        
        keyboard = [[InlineKeyboardButton("❌ Скасувати", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

    async def handle_story_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка розповіді з додатковою інформацією"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states:
            return
        
        # Отримуємо зібрану інформацію
        gender = self.user_states[user_id].get('gender', '🤐 Не вказано')
        group = self.user_states[user_id].get('group', '🤐 Не вказано')
        
        # Очищаємо стан
        del self.user_states[user_id]
        
        # Формуємо повідомлення для адміністраторів
        report_text = f"""
🆘 <b>АНОНІМНЕ ЗВЕРНЕННЯ</b>

📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M')}
👤 Від: Анонімний користувач
👦👧 Стать: {gender}
🏕️ Група: {group}

📝 <b>Повідомлення:</b>
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
            
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=update.message.photo[-1].file_id,
                    caption="📎 Фото до звернення"
                )
        except Exception as e:
            logger.error(f"Помилка відправки звернення: {e}")
        
        # Підтверджуємо користувачу
        confirmation_text = """
✅ <b>Дякуємо за твоє звернення!</b>

Ми отримали твоє повідомлення разом з додатковою інформацією. Тебе почули.

Дорослі, яким можна довіряти, допоможуть розібратися з ситуацією.

💚 Ти зробив/зробила правильно, що не мовчиш!
"""
        
        keyboard = [[InlineKeyboardButton("🔙 До головного меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            confirmation_text,
            reply_markup=reply_markup,
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
            [InlineKeyboardButton("🆘 SOS - Допомога анонімно", callback_data="sos_help")]
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
            if self.user_states[user_id].get('status') == "waiting_for_story":
                await self.handle_story_report(update, context)
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
        print("❌ Помилка: BOT_TOKEN не знайдено!")
        print("Встановіть змінну середовища BOT_TOKEN або створіть .env файл")
        return
    
    if not ADMIN_CHAT_ID:
        print("⚠️ Попередження: ADMIN_CHAT_ID не налаштовано. Анонімні звернення не працюватимуть.")
    
    # Створюємо екземпляр бота
    bot = CampSafetyBot()
    
    # Створюємо додаток
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Додаємо обробники
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("chatinfo", bot.get_chat_info))
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, bot.handle_message))
    
    # Запускаємо бота
    print("🤖 Бот 'Безпечний табір' запущено!")
    print("Натисніть Ctrl+C для зупинки")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()