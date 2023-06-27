from telebot import TeleBot
from telebot.types import *
from botutil import *

sugg_chat = -881724072
group_id = -1001912688972
settings = {
    "TOKEN": "6170839787:AAEK8E_BWQyuq7i-FAfrfeDJ4B_GvHmCwq8",
}

bot = TeleBot(settings["TOKEN"])
me = bot.get_me()
print(f"Logged in as\n{me.first_name}\n{me.id}\n@{me.username}")
init_db()


def render_markup(state: StatesEnum):
    if state == StatesEnum.Start:
        buttons = (KeyboardButton("Фото"), KeyboardButton("Текст"))
    elif state == StatesEnum.Photos:
        buttons = KeyboardButton("Текст")
    elif state == StatesEnum.Text:
        buttons = KeyboardButton("Фото")
    else:
        buttons = None

    return ReplyKeyboardMarkup(one_time_keyboard=True).add(*buttons)


@bot.message_handler(commands=["start"])
def index(message: Message):
    """Основной хендлер чата, начинается с комманды /start"""
    create_user(message.from_user.id, message.from_user.username, is_admin=False)
    bot.reply_to(
        message,
        "Привет! &#128075;\nДля того что бы отправить пост в предложку\nзаполните все пункты",
        reply_markup=render_markup(StatesEnum.Start),
        parse_mode="HTML",
    )
    suggestion = Suggestion()
    suggestion.uid = message.from_user.id
    bot.register_next_step_handler(message, states_logic, suggestion=suggestion)


@bot.callback_query_handler(func=lambda call: True)
def answer(call: CallbackQuery):
    """Отпрака в группу постов прошедших модерацию WIP"""
    # TODO!
    if call == StatesEnum.SendToGoup:
        bot.send_message(group_id, call.message.text)


def states_logic(message: Message, suggestion: Suggestion):
    """Не самая полезная штука, проверяет куда отправить некст сообщения"""
    if message.text == "Фото":
        bot.reply_to(
            message, "Отлично!\nМаксимум - 10 фотографий, не забывайте об этом"
        )
        bot.register_next_step_handler(message, parse_photos, suggestion)
    elif message.text == "Текст":
        bot.reply_to(message, "Отлично!\nТогда пришлите текст следующим сообщением!")
        bot.register_next_step_handler(message, parse_photos, suggestion=suggestion)
    else:
        bot.reply_to(message, "Ну и ладно, будем ждать вас снова(")


# На самом деле мой код тоже говно
# Если хочешь сделать заебись -- сделай нахуй 2 отдельных класса: Suggestion и SuggestionBuilder
# Suggestion -- mutable объект поста в предложке, создаётся и не меняется нахуй. Для него ебани то есть возможность
# загрузки из бд, сохранение в бд, отправку его в чат в телеге
# SuggestionBuilder -- объект уже который ты будешь передавать во все хендлеры. Я здесь тупо передавал сам
# Suggestion, но лучше их разделить, мало ли захочешь в них состояние какое-нибудь хранить (а ты потом захочешь).
# Он будет создаваться пустым, меняться в этом боте и у него будет функция build_suggestion, которая создат уже
# мьютабл Suggestion в конце. Будет збс


def parse_photos(message: Message, suggestion: Suggestion):
    """Парсинг фото. Надо попробовать сделать так, что бы он мог парсить еще и кучу фоток в одном соо"""
    # TODO!
    if message.content_type == "photo" and len(suggestion.photos) < 10:
        suggestion.photos.append(message.photo[-1].file_id)
        bot.reply_to(message, "Записал!")
        bot.register_next_step_handler(message, parse_photos, suggestion=suggestion)
    elif suggestion.text is None and message.content_type == "text":
        bot.reply_to(message, "Ну, видимо, хватит :D\nТеперь текст!")
        bot.register_next_step_handler(message, parse_text, suggestion=suggestion)
    else:
        suggestion.write()
        suggestion.send_to_redactors()
        bot.reply_to(message, f"Отлично, пост отправлен на обработку!")


def parse_text(message: Message, suggestion: Suggestion):
    suggestion.text = message.text
    if len(suggestion.photos) == 0:
        bot.reply_to(message, "Отлично, а теперь фото!")
        bot.register_next_step_handler(message, parse_photos, suggestioт=suggestion)
    else:
        suggestion.write()
        suggestion.send_to_redactors(bot)
        bot.reply_to(message, f"Отлично, пост отправлен на обработку!")


bot.infinity_polling()
