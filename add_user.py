import sqlite3

conn = sqlite3.connect("portfolios.db")
conn.execute("""
    INSERT INTO portfolio (uuid, name, bio, github, telegram, avatar, skills)
    VALUES (
        'real-001',
        'Rocket',
        'Python Developer',
        'https://github.com/rocket',
        '@rocket',
        'placeholder.png',
        'Python, Flask'
    )
""")
conn.commit()
conn.close()

print("Добавлен 1 реальный пользователь.")
