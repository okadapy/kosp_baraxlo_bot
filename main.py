from telebot import TeleBot
from telebot.types import *
from botutil import *

settings = {
    'TOKEN': "6170839787:AAEK8E_BWQyuq7i-FAfrfeDJ4B_GvHmCwq8",
}

bot = TeleBot(settings['TOKEN'])
init_db()


def render_markup(state: StatesEnum):
    if state == StatesEnum.Start:
        buttons = (KeyboardButton("Фото"), KeyboardButton("Текст"))
    elif state == StatesEnum.Photos:
        buttons = (KeyboardButton("Текст"))
    elif state == StatesEnum.Text:
        buttons = (KeyboardButton("Фото"))
    else: buttons = None

    return ReplyKeyboardMarkup(one_time_keyboard=True).add(*buttons)


@bot.message_handler(commands=["start"])
def index(message: Message):
    create_user(message.from_user.id, message.from_user.username)
    bot.reply_to(message, 'Привет! &#128075;\nДля того что бы отправить пост в предложку\nзаполните все пункты',
                 reply_markup=render_markup(StatesEnum.Start),
                 parse_mode="HTML")
    bot.register_next_step_handler(message, states_logic)


def states_logic(message: Message):
    photos = str()
    text = str()
    if message.text == "Фото":
        bot.reply_to(message, "Отлично!\nМаксимум - 10 фотографий, не забывайте об этом")
        bot.register_next_step_handler(message, parse_photos, photos)
    elif message.text == "Текст":
        bot.reply_to(message, "Отлично!\nТогда пришлите текст следующим сообщением!")
        bot.register_next_step_handler(message, parse_photos, text)
    else:
        bot.reply_to(message, "Ну и ладно, будем ждать вас снова(")
        bot.register_next_step_handler(message, index)

# Боже блять как же это плохо, канеда плз пофикси
# Нужно что бы у нас формировался текст и список фото через символ | и они как то друг с другом взаимодействовали так
# Что бы в итоге у нас выходило два значения - текст и фотки, которые потом надо запихнуть в инит саджешена.
# И оттуда записывались в бд. Я ебал, я спать
# def parse_photos(message: Message, callback: str, prev_step=None,):
#     if message.content_type == "photo" and len(callback.split("|")) < 10:
#         callback = callback + "|" + message.photo[-1].file_id
#         bot.reply_to(message, "Записал!")
#         bot.register_next_step_handler(message, parse_photos, callback=callback)
#     elif prev_step is None and message.content_type == "text":
#         text = str()
#         bot.reply_to(message, "Ну, видимо, хватит :D\nТеперь текст!")
#         bot.register_next_step_handler(message, parse_text, callback=text, prev_step=callback)
#     else:
#         Suggestion(prev_step, message.from_user.id, callback)
#
#
# def parse_text(message: Message, prev_step=None):
#     photos = str()
#     callback = message.text
#     if prev_step is None:
#         bot.reply_to(message, "Отлично, а теперь фото!")
#         bot.register_next_step_handler(message, parse_photos, callback=photos, prev_step=callback)
#     else:
#         Suggestion(callback, message.from_user.id, prev_step).write()


bot.infinity_polling()
