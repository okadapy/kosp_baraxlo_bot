from sqlite3 import connect
from time import ctime, time
import enum


class StatesEnum(enum.IntEnum):
    Start = 0
    Photos = 1
    Text = 2
    Exit = 999


class Suggestion(object):
    def __init__(self, text=None, uid=None, photos=None, date=ctime(time()), posted=False):
        self.text = text
        self.uid = uid
        self.photos = photos
        self.date = date
        self.posted = posted

    def write(self):
        con = connect("master.db")
        con.cursor().execute(
            f"INSERT OR IGNORE INTO suggestions "
            f"(text, uid, photos, date, posted) "
            f"VALUES ('{self.text}', {self.uid}, '{self.photos}', {self.date}, {self.posted})"
        )
        con.commit()
        con.close()




def read_suggestion(post_id) -> Suggestion:
    con = connect("master.db")
    res = con.cursor().execute(f"SELECT * FROM suggestions WHERE id = {post_id}").fetchone()
    return Suggestion(res[1], int(res[2]), res[3], res[4], True if "True" == res[5] else False)


def init_db():
    con = connect("master.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, "
        "uid LONG NOT NULL UNIQUE,"
        "uname TEXT NOT NULL,"
        "date TEXT);"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS suggestions(id INTEGER PRIMARY KEY,"
        "text TEXT,"
        "uid LONG NOT NULL,"
        "photos TEXT NOT NULL,"
        "date TEXT,"
        "posted BOOL NOT NULL);"
    )
    con.commit()
    con.close()


def create_user(uid: int, uname: str):
    con = connect("master.db")
    con.cursor().execute(
        f"INSERT OR IGNORE INTO users (uid, uname, date) VALUES ({uid}, '{uname}', '{ctime(time())}');"
    )
    con.commit()
    con.close()
