import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS high_scores
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               score INTEGER,
                               date TEXT)''')
        self.conn.commit()

    def insert_score(self, score):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO high_scores (score, date) VALUES (?, ?)", (score, date))
        self.conn.commit()

    def get_high_score(self):
        self.cursor.execute("SELECT MAX(score) FROM high_scores")
        result = self.cursor.fetchone()
        return result[0] if result[0] is not None else 0

    def get_top_scores(self, limit=10):
        self.cursor.execute("SELECT score, date FROM high_scores ORDER BY score DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()