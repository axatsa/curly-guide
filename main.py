import telebot
from telebot import types

API_TOKEN = '5926697072:AAGx_FVYK4LC5fm1c9_k7_SLQ9uZb7F_dMY'
chat_id = -1003171608196
bot = telebot.TeleBot(API_TOKEN)

# Внутрипроцессное хранилище состояний пользователей (сложно для продакшена, но просто для Telegram бота)
user_state = {}


def get_feedback_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Положительный отзыв"),
        types.KeyboardButton("Жалоба"),
        types.KeyboardButton("Предложение")
    )
    return keyboard


def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Приветствую вас в боте ....\nЗдесь вы можете оставить как положительный, так и отрицательный отзыв!\n "
        "Будем рады вашим пожеланиям, предложениям или жалобам.",
        reply_markup=get_feedback_keyboard()
    )
def again(message):
    bot.send_message(
        message.chat.id,
        "Что нибудь еще?",
        reply_markup=get_feedback_keyboard()

    )

@bot.message_handler(commands=['help', 'start'])
def on_start(message):
    send_welcome(message)


@bot.message_handler(func=lambda message: message.text in ["Положительный отзыв", "Жалоба", "Предложение"])
def handle_feedback_buttons(message):
    user_state[message.from_user.id] = message.text  # Запоминаем выбранную категорию
    if message.text == "Положительный отзыв":
        bot.send_message(message.chat.id, "Пожалуйста, напишите ваш положительный отзыв.")
    elif message.text == "Жалоба":
        bot.send_message(message.chat.id, "Опишите вашу жалобу, мы обязательно рассмотрим её.")
    elif message.text == "Предложение":
        bot.send_message(message.chat.id, "Напишите ваше предложение, нам важно ваше мнение!")
    else:
        bot.send_message(message.chat.id, "Неизвестная команда, используйте предложенные кнопки")


@bot.message_handler(
    func=lambda message: user_state.get(message.from_user.id, None) in ["Положительный отзыв", "Жалоба", "Предложение"])
def handle_feedback_text(message):
    feedback_type = user_state.pop(message.from_user.id)
    text_for_group = (
        f"Получено: {feedback_type.lower()}\n"
        f"От пользоваеля: @{message.from_user.username if message.from_user.username else message.from_user.first_name}\n"
        f"Текст: {message.text}\n"

    )
    bot.send_message(
        chat_id,
        text_for_group
    )

    bot.send_message(
        message.chat.id,
        f"Спасибо за ваш {feedback_type.lower()}!\nВаше сообщение получено."
    )
    again(message)


bot.infinity_polling()
