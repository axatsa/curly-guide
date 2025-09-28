import telebot
from telebot import types

API_TOKEN = "5926697072:AAEEzRzJHFxijPCrCBNgZsYHkrPhxE-mdeg"
GROUP_CHAT_ID = -1003167500913

bot = telebot.TeleBot(API_TOKEN)
user_state = {}

# Стадии
STAGE_LANG = "LANG"
STAGE_CATEGORY = "CATEGORY"
STAGE_INPUT = "INPUT"
STAGE_CONTACT_OPTION = "CONTACT_OPTION"
STAGE_WAIT_CONTACT = "WAIT_CONTACT"

# Кнопки
RU_LANG_BTN = "Русский"
UZ_LANG_BTN = "O'zbekcha"
RU_CATS = ["Жалоба", "Предложение"]
UZ_CATS = ["Shikoyat", "Taklif"]
RU_BACK = "Назад"
UZ_BACK = "Orqaga"

RU_SEND_WITHOUT_CONTACT = "Отправить сообщение без контакта"
RU_SEND_WITH_CONTACT = "Отправить сообщение с контактом"
UZ_SEND_WITHOUT_CONTACT = "Kontaktsiz yuborish"
UZ_SEND_WITH_CONTACT = "Kontakt bilan yuborish"

TEXTS = {
    "welcome_first": {
        "ru": "🇷🇺 Здравствуйте! Я помощник по работе с предложениями и жалобами в Thompson International School.\n\nПожалуйста, выберите язык: ",
        "uz": "🇺🇿 Assalomu alaykum! Thompson International School taklif va shikoyatlar bo‘yicha yordamchisiman.\n\nIltimos, tilni tanlang:"
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
    "contact_option": {
        "ru": "Как вы хотите отправить своё сообщение?",
        "uz": "Xabaringizni qanday yuborishni xohlaysiz?"
    },
    "send_success": {
        "ru": "Благодарим вас за отзыв!\n\nКаждый отзыв помогает нам становиться лучше. Мы обязательно рассмотрим вашу заявку.",
        "uz": "Fikringiz uchun tashakkur! Har bir fikr bizning yanada yaxshilanishimizga yordam beradi. Murojaatingiz ko‘rib chiqiladi."
    },
    "contact_request": {
        "ru": "Пожалуйста, поделитесь контактом для обратной связи:",
        "uz": "Iltimos, bog‘lanish uchun kontaktingizni ulashing:"
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


def get_category_keyboard(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cats = RU_CATS if lang == "ru" else UZ_CATS
    back = RU_BACK if lang == "ru" else UZ_BACK
    kb.add(*[types.KeyboardButton(c) for c in cats])
    # kb.add(types.KeyboardButton(back))  # можно добавить назад, если требуется
    return kb


def get_back_keyboard(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(RU_BACK if lang == "ru" else UZ_BACK))
    return kb


def get_contact_option_keyboard(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if lang == "ru":
        btn1 = RU_SEND_WITHOUT_CONTACT
        btn2 = RU_SEND_WITH_CONTACT
    else:
        btn1 = UZ_SEND_WITHOUT_CONTACT
        btn2 = UZ_SEND_WITH_CONTACT
    kb.row(types.KeyboardButton(btn1), types.KeyboardButton(btn2))
    return kb


def get_contact_keyboard(lang):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    text = "Оставить контакт" if lang == "ru" else "Kontakt qoldirish"
    kb.add(types.KeyboardButton(text, request_contact=True))
    return kb


def user_step(user_id):
    return user_state.get(user_id, {}).get("stage", None)


def set_state(user_id, **kwargs):
    user_state.setdefault(user_id, {}).update(**kwargs)


def reset_state(user_id):
    if user_id in user_state:
        user_state[user_id] = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    set_state(user_id, stage=STAGE_LANG)
    bot.send_message(user_id, TEXTS["welcome_first"]["ru"] + "\n\n" + TEXTS["welcome_first"]["uz"],
                     reply_markup=get_lang_keyboard())


@bot.message_handler(func=lambda m: user_step(m.from_user.id) == STAGE_LANG)
def handle_lang(message):
    user_id = message.from_user.id
    if message.text == RU_LANG_BTN:
        set_state(user_id, lang="ru", stage=STAGE_CATEGORY)
        bot.send_message(user_id, TEXTS["choose_category"]["ru"], reply_markup=get_category_keyboard("ru"))
    elif message.text == UZ_LANG_BTN:
        set_state(user_id, lang="uz", stage=STAGE_CATEGORY)
        bot.send_message(user_id, TEXTS["choose_category"]["uz"], reply_markup=get_category_keyboard("uz"))
    else:
        bot.send_message(user_id, TEXTS["unknown_command"]["ru"], reply_markup=get_lang_keyboard())


@bot.message_handler(func=lambda m: user_step(m.from_user.id) == STAGE_CATEGORY)
def handle_category(message):
    user_id = message.from_user.id
    lang = user_state[user_id]["lang"]
    cat_map = RU_CATS if lang == "ru" else UZ_CATS
    if message.text in cat_map:
        set_state(user_id, category=message.text, stage=STAGE_INPUT)
        prompt = TEXTS["enter_complaint"][lang] if message.text == cat_map[0] else TEXTS["enter_suggestion"][lang]
        bot.send_message(user_id, prompt, reply_markup=get_back_keyboard(lang))
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
    set_state(user_id, feedback=message.text, stage=STAGE_CONTACT_OPTION)
    bot.send_message(user_id, TEXTS["contact_option"][lang], reply_markup=get_contact_option_keyboard(lang))


@bot.message_handler(func=lambda m: user_step(m.from_user.id) == STAGE_CONTACT_OPTION)
def handle_send_option(message):
    user_id = message.from_user.id
    lang = user_state[user_id]["lang"]
    with_contact = False
    if ((lang == "ru" and message.text == RU_SEND_WITHOUT_CONTACT) or
            (lang == "uz" and message.text == UZ_SEND_WITHOUT_CONTACT)):
        # Отправить без контакта
        send_feedback(user_id, with_contact=False)
    elif ((lang == "ru" and message.text == RU_SEND_WITH_CONTACT) or
          (lang == "uz" and message.text == UZ_SEND_WITH_CONTACT)):
        # Запросить контакт и отправить с ним
        set_state(user_id, stage=STAGE_WAIT_CONTACT)
        bot.send_message(user_id, TEXTS["contact_request"][lang], reply_markup=get_contact_keyboard(lang))
    else:
        bot.send_message(user_id, TEXTS["unknown_command"][lang], reply_markup=get_contact_option_keyboard(lang))


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = message.from_user.id
    stage = user_step(user_id)
    if stage != STAGE_WAIT_CONTACT:
        return
    set_state(user_id, contact=message.contact.phone_number)
    send_feedback(user_id, with_contact=True)


def send_feedback(user_id, with_contact):
    data = user_state[user_id]
    lang = data["lang"]
    category = data["category"]
    feedback_txt = data["feedback"]
    contact = data.get("contact", "") if with_contact else ""
    user_name = bot.get_chat(user_id).username or bot.get_chat(user_id).first_name

    # Создать текст для группы
    text_for_group = (
        f"📌 Уведомление от Thompson International School Bot\n"
        f"🇷🇺🇺🇿 Язык:   [{lang.upper()}]\n"
        f"📬 Тип: {category}\n"
        f"🖊 От:  @{user_name},\n"
        f"☎️ Номер телефона:  {contact if contact else 'Не предоставлен'}\n"
        f"🔖 Описание:\n{feedback_txt}"
    )
    bot.send_message(GROUP_CHAT_ID, text_for_group)
    # Благодарим пользователя
    bot.send_message(user_id, TEXTS["send_success"][lang], reply_markup=get_category_keyboard(lang))
    # Сбросить только этап (оставить язык для повтора)
    set_state(user_id, stage=STAGE_CATEGORY)
    # Не сбрасываем контакт: его можно обновить!


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
