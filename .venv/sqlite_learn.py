import sqlite3 as sq

with sq.connect("sanek.db") as con:
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users1(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            sex INTEGER,
            old INTEGER,
            score INTEGER
            )""")
    cur.execute("INSERT INTO users1(name, score) VALUES(?, ?)", ("crow", 1002))
    cur.execute("SELECT * FROM users1")
    for res in cur:
        print(res)






