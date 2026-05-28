import sqlite3

conn = sqlite3.connect("portfolios.db")
conn.execute("DELETE FROM portfolio WHERE id = (SELECT MAX(id) FROM portfolio)")
conn.commit()
print("Последний пользователь удалён")