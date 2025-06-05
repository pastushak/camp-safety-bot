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
            [InlineKeyboardButton("🆘 SOS - Допомога анонімно", callback_data="sos_help")]
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
        elif query.data == "urgent_help":
            await self.urgent_help(query, context)
        elif query.data == "need_help":
            await self.need_help(query)
        elif query.data == "want_to_share":
            await self.want_to_share(query)
        elif query.data == "back_to_menu":
            await self.back_to_menu(query)
        elif query.data == "back_to_sos":
            await self.sos_help_menu(query)
        elif query.data == "cant_write_now":
            await self.cant_write_now(query, context)

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

<b>4. Звернись за допомогою анонімно</b>
🔸 Використай розділ "SOS - Допомога анонімно"
🔸 Ми побачимо твоє повідомлення й допоможемо

<b>5. Пам'ятай: ти не винен/винна</b>
🔸 Кожен має право на повагу та безпеку!
"""
        
        keyboard = [
            [InlineKeyboardButton("🆘 SOS - Допомога анонімно", callback_data="sos_help")],
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

👋 Тут ти можеш безпечно розповісти про ситуацію, яка тебе турбує.
Ми не питаємо, як тебе звати. Це <b>повністю анонімно</b>.

Оцини рівень ситуації, щоб ми могли швидше допомогти:

🔴 <b>Термінова допомога!</b>
Якщо зараз щось відбувається або ти в небезпеці

🟡 <b>Потрібна допомога</b>  
Щось сталося і потрібне втручання дорослих

🟢 <b>Хочу поділитися</b>
Хочу розповісти про ситуацію або отримати пораду
"""
        
        keyboard = [
            [InlineKeyboardButton("🔴 Термінова допомога!", callback_data="urgent_help")],
            [InlineKeyboardButton("🟡 Потрібна допомога", callback_data="need_help")],
            [InlineKeyboardButton("🟢 Хочу поділитися", callback_data="want_to_share")],
            [InlineKeyboardButton("🔙 Назад до меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def urgent_help(self, query, context):
        """Термінова допомога"""
        user_id = query.from_user.id
        
        # Відправляємо екстрене повідомлення адміністраторам
        urgent_text = f"""
🔴 <b>🚨 ТЕРМІНОВА ДОПОМОГА! 🚨</b>

📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M')}
👤 Від: Анонімний користувач
🆘 Потрібна НЕГАЙНА допомога!

⚠️ ТЕРМІНОВО ЗВЕРНІТЬ УВАГУ!
Дитина обрала "Термінова допомога" - ситуація критична!
"""
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=urgent_text,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Помилка відправки терміновоїо SOS: {e}")
        
        # Встановлюємо стан для детального опису
        self.user_states[user_id] = "waiting_for_urgent_details"
        
        text = """
🔴 <b>Термінова допомога</b>

🚨 Ми отримали твій сигнал про терміновість!
Дорослі вже сповіщені і приділять цьому максимальну увагу.

Коротко опиши що відбувається зараз або що сталося:
• Де це відбувається?
• Хто задіяний?
• Що саме відбувається?

Якщо не можеш писати - не хвилюйся, дорослі вже шукають спосіб допомогти.

✍️ <b>Напиши наступним повідомленням що сталося.</b>
"""
        
        keyboard = [
            [InlineKeyboardButton("🚫 Не можу писати зараз", callback_data="cant_write_now")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_sos")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def need_help(self, query):
        """Потрібна допомога"""
        text = """
🟡 <b>Потрібна допомога</b>

👋 Ми готові тебе вислухати і допомогти.
Розкажи детально про ситуацію:

📝 <b>Напиши про:</b>
• Що сталося?
• Коли це відбувається?
• Хто задіяний?
• У якій групі?
• Як довго це триває?
• Будь-які інші важливі деталі

Можеш також надіслати фото чи скріншот, якщо це допоможе.

✍️ <b>Просто напиши наступним повідомленням свою історію.</b>
"""
        
        # Встановлюємо стан користувача
        user_id = query.from_user.id
        self.user_states[user_id] = "waiting_for_help_report"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_sos")],
            [InlineKeyboardButton("❌ Скасувати", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def want_to_share(self, query):
        """Хочу поділитися"""
        text = """
🟢 <b>Хочу поділитися</b>

💚 Дякуємо, що довіряєш нам!
Ділитися своїми переживаннями - це важливо.

📝 <b>Розкажи про:</b>
• Що тебе турбує?
• Можливо щось бачив/бачила?
• Потрібна порада?
• Хочеш просто висловитися?

Ми прочитаємо і, можливо, зможемо дати пораду або просто підтримати.

✍️ <b>Напиши наступним повідомленням що хочеш розповісти.</b>
"""
        
        # Встановлюємо стан користувача
        user_id = query.from_user.id
        self.user_states[user_id] = "waiting_for_sharing"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_sos")],
            [InlineKeyboardButton("❌ Скасувати", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def handle_urgent_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка деталей терміновоїі допомоги"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states or self.user_states[user_id] != "waiting_for_urgent_details":
            return
        
        del self.user_states[user_id]
        
        # Відправляємо деталі адміністраторам
        details_text = f"""
🔴 <b>🚨 ДЕТАЛІ ТЕРМІНОВОЇІ СИТУАЦІЇ 🚨</b>

📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M')}
📝 Додаткова інформація:

{update.message.text}

⚠️ КРИТИЧНА СИТУАЦІЯ - НЕГАЙНА РЕАКЦІЯ ПОТРІБНА!
"""
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=details_text,
                parse_mode=ParseMode.HTML
            )
            
            # Якщо є фото
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=update.message.photo[-1].file_id,
                    caption="📎 Фото до терміновоїі ситуації"
                )
        except Exception as e:
            logger.error(f"Помилка відправки деталей терміновоїі допомоги: {e}")
        
        # Підтверджуємо користувачу
        confirmation_text = """
✅ <b>Інформацію передано!</b>

🚨 Дорослі отримали всі деталі ситуації.
Допомога вже йде до тебе!

Тримайся і пам'ятай - ти не один/одна.
💚 Ти правильно зробив/зробила, що звернувся за допомогою!
"""
        
        keyboard = [[InlineKeyboardButton("🔙 До головного меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            confirmation_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

    async def handle_help_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка звернення за допомогою"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states or self.user_states[user_id] != "waiting_for_help_report":
            return
        
        # Очищаємо стан
        del self.user_states[user_id]
        
        # Формуємо повідомлення для адміністраторів
        report_text = f"""
🟡 <b>ЗВЕРНЕННЯ ЗА ДОПОМОГОЮ</b>

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
                    caption="📎 Фото до звернення за допомогою"
                )
        except Exception as e:
            logger.error(f"Помилка відправки звернення: {e}")
        
        # Підтверджуємо користувачу
        confirmation_text = """
✅ <b>Дякуємо за звернення!</b>

Ми отримали твоє повідомлення. Тебе почули.

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

    async def handle_sharing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка ділення думками"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_states or self.user_states[user_id] != "waiting_for_sharing":
            return
        
        # Очищаємо стан
        del self.user_states[user_id]
        
        # Формуємо повідомлення для адміністраторів
        sharing_text = f"""
🟢 <b>ДІЛЕННЯ ДУМКАМИ</b>

📅 Час: {datetime.now().strftime('%d.%m.%Y %H:%M')}
👤 Від: Анонімний користувач
💭 Повідомлення:

{update.message.text}

---
💚 Інформаційне повідомлення
"""
        
        # Відправляємо в адмін-чат
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=sharing_text,
                parse_mode=ParseMode.HTML
            )
            
            # Якщо є фото/документи
            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=update.message.photo[-1].file_id,
                    caption="📎 Фото до ділення думками"
                )
        except Exception as e:
            logger.error(f"Помилка відправки ділення думками: {e}")
        
        # Підтверджуємо користувачу
        confirmation_text = """
💚 <b>Дякуємо, що поділився!</b>

Ми прочитали твоє повідомлення. 

Дякуємо за довіру! Ділитися своїми думками і переживаннями - це дуже важливо.

Якщо ситуація зміниться і потрібна буде допомога - завжди звертайся!
"""
        
        keyboard = [[InlineKeyboardButton("🔙 До головного меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            confirmation_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    async def cant_write_now(self, query, context):
        """Обробка "Не можу писати зараз" """
        
        text = """
    ✅ <b>Зрозуміло!</b>

    🚨 Дорослі вже знають, що тобі потрібна термінова допомога.
    Вони зараз шукають спосіб тебе знайти і допомогти.

    🛡️ <b>Що робити зараз:</b>
    - Спробуй знайти безпечне місце
    - Будь поруч з дорослими, яким довіряєш
    - Якщо зможеш пізніше - напиши боту ще раз

    💚 Тримайся! Допомога вже йде!
    """

        keyboard = [
            [InlineKeyboardButton("📞 Спробую знайти дорослого", callback_data="back_to_menu")],
            [InlineKeyboardButton("💬 Все ж таки напишу", callback_data="urgent_help")]
        ]

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
            if self.user_states[user_id] == "waiting_for_urgent_details":
                await self.handle_urgent_details(update, context)
            elif self.user_states[user_id] == "waiting_for_help_report":
                await self.handle_help_report(update, context)
            elif self.user_states[user_id] == "waiting_for_sharing":
                await self.handle_sharing(update, context)
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