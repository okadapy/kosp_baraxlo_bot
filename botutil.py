from sqlite3 import connect
from time import ctime, time
import enum
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class StatesEnum(enum.IntEnum):
    Start = 0
    Photos = 1
    Text = 2
    SendToGoup = 10
    DeleteFromSugg = 11
    Exit = 999


class Suggestion(object):
    sugg_chat = -881724072
    group_id = -1001912688972

    def __init__(
            self, text=None, uid=None, photos=None, date=ctime(time()), posted=False
    ):
        if photos is None:
            photos = list()
        self.text = text
        self.uid = uid
        self.photos = photos
        self.date = date
        self.posted = posted

    def photos_str(self):
        """Строка фотографий на основе списка для записи в БД"""
        if len(self.photos) == 0:
            return ""
        s = self.photos[0]
        for r in self.photos[1:]:
            s += "|"
            s += r
        return s

    def write(self):
        """Запись предложки в БД"""
        # TODO! Отлетает из за OUTPUT, а мне хочется все же айдишник предложи вытащить, что бы ее можно было постить.
        # Если есть мысли как это сделать иначе - пиши.
        con = connect("master.db")
        res = con.cursor().execute(
            f"INSERT OR IGNORE INTO suggestions "
            f"(text, uid, photos, date, posted) OUTPUT INSERTED.id"
            f"VALUES ('{self.text}', {self.uid}, '{self.photos_str()}', '{self.date}', {self.posted})"
        ).fetchone()
        self.id = res[0]
        con.commit()
        con.close()

    def send_to_redactors(self, bot: TeleBot):
        """Отправка в конфу редачей, работает через жопу"""
        # TODO!
        for j in self.photos:
            bot.send_photo(photo=j, chat_id=self.sugg_chat)
        buttons = (
            InlineKeyboardButton("Отправить", callback_data={"state": StatesEnum.SendToGoup, "id": self.id}),
            InlineKeyboardButton("Удалить", callback_data={"state": StatesEnum.DeleteFromSugg, "id": self.id})
        )
        bot.send_message(
            self.sugg_chat, self.text, reply_markup=InlineKeyboardMarkup().add(*buttons)
        )


def read_suggestion(post_id) -> Suggestion:
    """Выгрузка саджа из предложки, не проверялась"""
    con = connect("master.db")
    res = (
        con.cursor()
        .execute(f"SELECT * FROM suggestions WHERE id = {post_id}")
        .fetchone()
    )
    return Suggestion(
        res[1], int(res[2]), res[3], res[4], True if "True" == res[5] else False
    )


def init_db():
    con = connect("master.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, "
        "uid LONG NOT NULL UNIQUE,"
        "uname TEXT NOT NULL,"
        "date TEXT NOT NULL,"
        "is_admin BOOL NOT NULL);"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS suggestions(id INTEGER PRIMARY KEY,"
        "text TEXT,"
        "uid LONG NOT NULL,"
        "photos TEXT NOT NULL,"
        "date TEXT NOT NULL,"
        "posted BOOL NOT NULL);"
    )
    con.commit()
    con.close()


def create_user(uid: int, uname: str, is_admin=False):
    """Создание нью пользователя"""
    con = connect("master.db")
    con.cursor().execute(
        f"INSERT OR IGNORE INTO users (uid, uname, date, is_admin) VALUES ({uid}, '{uname}', '{ctime(time())}', {is_admin});"
    )
    con.commit()
    con.close()
