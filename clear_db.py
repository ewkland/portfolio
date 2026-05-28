import sqlite3

conn = sqlite3.connect("portfolios.db")
conn.execute("DELETE FROM portfolio;")
conn.commit()
conn.close()

print("Таблица очищена!")
