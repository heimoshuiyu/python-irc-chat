import sqlite3
import hashlib


class Database:
    def __init__(self, db):
        self.salt = 'defaultSalt'
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS users (nickname text PRIMARY KEY, password text)")
        self.conn.commit()

    def register(self, nickname, password):
        self.cur.execute(
            "INSERT OR IGNORE INTO users VALUES (?, ?)", (nickname, password))
        self.conn.commit()

    def login(self, nickname, password):
        if self.exists(nickname):
            self.cur.execute(
                "SELECT * FROM users WHERE nickname=? AND password=?", (nickname, password))
            return self.cur.fetchone() is not None
        else:
            self.register(nickname, password)
            return True

    def delete(self, nickname):
        self.cur.execute("DELETE FROM users WHERE nickname=?", (nickname,))
        self.conn.commit()

    def exists(self, nickname):
        self.cur.execute("SELECT * FROM users WHERE nickname=?", (nickname,))
        return self.cur.fetchone() is not None

    def __del__(self):
        self.conn.close()

    def dump(self):
        self.cur.execute("SELECT * FROM users")
        return self.cur.fetchall()

    def generateHash(self, password, salt):
        return hashlib.sha256(password.encode() + salt.encode()).hexdigest()


userDbName = "users.db"
