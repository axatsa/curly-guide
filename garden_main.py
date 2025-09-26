import telebot
from telebot import types

API_TOKEN = "TOKEN"
GROUP_CHAT_ID = -1003173960299

bot = telebot.TeleBot(API_TOKEN)

user_state = {}

# Этапы
STAGE_LANG = "LANG"
STAGE_CONTACT = "CONTACT"
STAGE_CATEGORY = "CATEGORY"
STAGE_INPUT = "INPUT"

# Кнопки
RU_LANG_BTN = "Русский"
UZ_LANG_BTN = "O'zbekcha"
RU_CATS = ["Жалоба", "Предложение"]
UZ_CATS = ["Shikoyat", "Taklif"]
RU_BACK = "Назад"
UZ_BACK = "Orqaga"

TEXTS = {
    "welcome_first": {
        "ru": "Здравствуйте! Я помощник по работе с предложениями и жалобами в Thompson Land.\n\nПожалуйста, выберите язык:",
        "uz": "Assalomu alaykum! Men Thompson Land taklif va shikoyatlar bo‘yicha yordamchisiman.\n\nIltimos, tilni tanlang:"
    },
    "contact": {
        "ru": "Оставьте, пожалуйста, свой контакт, чтобы мы могли с вами связаться:",
        "uz": "Iltimos, biz siz bilan bog‘lana olishimiz uchun kontaktingizni qoldiring:"
    },
    "choose_category": {
        "ru": "Выберите, что вы хотите нам сообщить:",
        "uz": "Nimani bizga bildirmoqchisiz?"
    },
    "enter_complaint": {
        "ru": "Введите, пожалуйста, свою жалобу:",
        "uz": "Iltimos, shikoyatingizni yozing:"
    },
    "enter_suggestion": {
        "ru": "Введите, пожалуйста, своё предложение:",
        "uz": "Iltimos, taklifingizni yozing:"
    },
    "thanks": {
        "ru": "Благодарим вас за отзыв!\n\nКаждый отзыв помогает нам становиться лучше. Мы обязательно свяжемся с вами.",
        "uz": "Fikringiz uchun tashakkur!\n\nHar bir fikr bizning yanada yaxshilanishimizga yordam beradi. Biz albatta siz bilan bog‘lanamiz."
    },
    "choose_category_repeat": {
        "ru": "Здравствуйте! Выберите, что вы хотите нам сообщить:",
        "uz": "Assalomu alaykum! Bizga nimani bildirmoqchisiz?"
    },
    "unknown_command": {
        "ru": "Пожалуйста, используйте кнопки",
        "uz": "Iltimos, tugmalardan foydalaning"
    }
}


def get_lang_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(RU_LANG_BTN), types.KeyboardButton(UZ_LANG_BTN))
    return kb


def get_contact_keyboard(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    text = "Оставить контакт" if lang == "ru" else "Kontakt qoldirish"
    kb.add(types.KeyboardButton(text, request_contact=True))
    return kb


def get_category_keyboard(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cats = RU_CATS if lang == "ru" else UZ_CATS
    back = RU_BACK if lang == "ru" else UZ_BACK
    kb.add(*[types.KeyboardButton(c) for c in cats])
    kb.add(types.KeyboardButton(back))
    return kb


def get_back_keyboard(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(RU_BACK if lang == "ru" else UZ_BACK))
    return kb


def user_step(user_id):
    return user_state.get(user_id, {}).get("stage", None)


def set_state(user_id, **kwargs):
    user_state.setdefault(user_id, {}).update(**kwargs)


def reset_state(user_id):
    if user_id in user_state:
        user_state[user_id] = {}  # полностью сбросить


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    state = user_state.get(user_id, {})
    if "lang" not in state:
        # Первый запуск
        set_state(user_id, stage=STAGE_LANG)
        bot.send_message(user_id, TEXTS["welcome_first"]["ru"] + "\n\n" + TEXTS["welcome_first"]["uz"],
                         reply_markup=get_lang_keyboard())
    elif "contact" not in state:
        # Язык выбран, но нет контакта
        set_state(user_id, stage=STAGE_CONTACT)
        lang = state.get("lang", "ru")
        bot.send_message(user_id, TEXTS["contact"][lang], reply_markup=get_contact_keyboard(lang))
    else:
        # Повторный старт, язык и контакт есть
        lang = state["lang"]
        set_state(user_id, stage=STAGE_CATEGORY)
        bot.send_message(user_id, TEXTS["choose_category_repeat"][lang], reply_markup=get_category_keyboard(lang))


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    stage = user_step(user_id)
    if stage != STAGE_CONTACT:
        return
    contact = message.contact.phone_number
    set_state(user_id, contact=contact, stage=STAGE_CATEGORY)
    lang = user_state[user_id]["lang"]
    bot.send_message(user_id, TEXTS["choose_category"][lang], reply_markup=get_category_keyboard(lang))


@bot.message_handler(func=lambda m: user_step(m.from_user.id) == STAGE_LANG)
def handle_lang(message):
    user_id = message.from_user.id
    if message.text == RU_LANG_BTN:
        set_state(user_id, lang="ru", stage=STAGE_CONTACT)
        bot.send_message(user_id, TEXTS["contact"]["ru"], reply_markup=get_contact_keyboard("ru"))
    elif message.text == UZ_LANG_BTN:
        set_state(user_id, lang="uz", stage=STAGE_CONTACT)
        bot.send_message(user_id, TEXTS["contact"]["uz"], reply_markup=get_contact_keyboard("uz"))
    else:
        bot.send_message(user_id, TEXTS["unknown_command"]["ru"], reply_markup=get_lang_keyboard())


@bot.message_handler(func=lambda m: user_step(m.from_user.id) == STAGE_CATEGORY)
def handle_category(message):
    user_id = message.from_user.id
    lang = user_state[user_id]["lang"]
    back = RU_BACK if lang == "ru" else UZ_BACK
    if message.text in (RU_CATS if lang == "ru" else UZ_CATS):
        set_state(user_id, category=message.text, stage=STAGE_INPUT)  # Жалоба/шик.
        prompt = TEXTS["enter_complaint"][lang] if message.text in [RU_CATS[0], UZ_CATS[0]] else \
        TEXTS["enter_suggestion"][lang]
        bot.send_message(user_id, prompt, reply_markup=get_back_keyboard(lang))
    elif message.text == back:
        # Вернуть на этап указания контакта
        set_state(user_id, stage=STAGE_CONTACT)
        bot.send_message(user_id, TEXTS["contact"][lang], reply_markup=get_contact_keyboard(lang))
    else:
        bot.send_message(user_id, TEXTS["unknown_command"][lang], reply_markup=get_category_keyboard(lang))


@bot.message_handler(func=lambda m: user_step(m.from_user.id) == STAGE_INPUT)
def handle_input(message):
    user_id = message.from_user.id
    lang = user_state[user_id]["lang"]
    back = RU_BACK if lang == "ru" else UZ_BACK
    if message.text == back:
        set_state(user_id, stage=STAGE_CATEGORY)
        bot.send_message(user_id, TEXTS["choose_category"][lang], reply_markup=get_category_keyboard(lang))
        return
    category = user_state[user_id]["category"]
    contact = user_state[user_id].get("contact", "")
    user_name = message.from_user.username or message.from_user.first_name
    feedback_txt = message.text

    # Формируем сообщение для группы
    text_for_group = (
        f"NEW Thompson LAND FEEDBACK [{lang.upper()}]\n"
        f"Тип: {category}\n"
        f"От: @{user_name}, Тел: {contact}\n"
        f"Текст:\n{feedback_txt}"
    )
    bot.send_message(GROUP_CHAT_ID, text_for_group)

    # Благодарим пользователя
    bot.send_message(user_id, TEXTS["thanks"][lang], reply_markup=get_category_keyboard(lang))
    set_state(user_id, stage=STAGE_CATEGORY)
    # flush введённый category – чтобы дать выбрать заново
    # Не сбрасываем язык/контакт


@bot.message_handler(func=lambda m: True)
def default_handler(message):
    user_id = message.from_user.id
    state = user_state.get(user_id, {})
    lang = state.get("lang", "ru")
    stage = state.get("stage", None)
    if not stage:
        handle_start(message)
    else:
        bot.send_message(user_id, TEXTS["unknown_command"][lang])


if __name__ == "__main__":
    bot.infinity_polling()
