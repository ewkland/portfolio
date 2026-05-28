import sqlite3
import uuid

import requests
from flask import Flask, redirect, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

tool_icons = {
    "Python": "🐍", "Flask": "🌶️", "HTML": "📄", "CSS": "🎨", "HTML/CSS": "✏️",
    "Git": "🔧", "GitHub": "🐙", "Telegram": "✈️", "Телеграм": "✈️",
    "SQL": "🗃️", "SQLite": "🟦", "JavaScript": "⚡", "JS": "⚡", "Jinja": "🧩",
}


def get_db():
    conn = sqlite3.connect("portfolios.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            name TEXT,
            bio TEXT,
            github TEXT,
            telegram TEXT,
            avatar TEXT,
            skills TEXT
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def all_portfolios():
    conn = get_db()
    portfolios = conn.execute("SELECT * FROM portfolio").fetchall()
    conn.close()

    filter_skill = request.args.get("skill")
    if filter_skill:
        filter_skill = filter_skill.strip().lower()
    else:
        filter_skill = None

    profiles = []
    for portfolio in portfolios:
        skills_list = [s.strip() for s in portfolio["skills"].split(",") if s.strip()]
        profiles.append({
            "name": portfolio["name"],
            "bio": portfolio["bio"],
            "github": portfolio["github"],
            "telegram": portfolio["telegram"],
            "avatar": portfolio["avatar"],
            "skills": skills_list,
            "uuid": portfolio["uuid"],
        })

    portfolios = profiles

    filter_skill = request.args.get("skill")
    if filter_skill:
        filter_skill = filter_skill.strip()
        portfolios = [p for p in portfolios
                      if filter_skill in [s.strip() for s in p["skills"]]]
    else:
        filter_skill = ""

    return render_template(
        "all_portfolios.html",
        portfolios=portfolios,
        tool_icons=tool_icons,
        current_skill=filter_skill,
    )


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate():
    form_data = request.form
    avatar = request.files.get("avatar")

    uid = str(uuid.uuid4())

    avatar_filename = ""
    if avatar and avatar.filename:
        filename = secure_filename(f"{uid}_{avatar.filename}")
        avatar_path = f"static/uploads/{filename}"
        avatar.save(avatar_path)
        avatar_filename = avatar_path.replace("static/", "")

    github = (
        form_data["github"]
        .strip()
        .replace("https://github.com/", "")
        .replace("/", "")
    )

    conn = get_db()
    conn.execute(
        """
        INSERT INTO portfolio (uuid, name, bio, github, telegram, avatar, skills)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid,
            form_data["name"],
            form_data["bio"],
            github,
            form_data["telegram"],
            avatar_filename,
            form_data["skills"],
        ),
    )
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/portfolio/<uuid>")
def view_portfolio(uuid):
    conn = get_db()
    portfolio = conn.execute(
        "SELECT * FROM portfolio WHERE uuid = ?", (uuid,)
    ).fetchone()
    conn.close()

    if not portfolio:
        return "Портфолио не найдено", 404

    name = portfolio["name"]
    bio = portfolio["bio"]
    github = portfolio["github"]
    telegram = portfolio["telegram"]
    avatar = portfolio["avatar"]
    skills = [s.strip() for s in portfolio["skills"].split(",")]

    projects = []
    try:
        url = f"https://api.github.com/users/{github}/repos"
        response = requests.get(url)
        if response.ok:
            repos = response.json()[:6]
            for repo in repos:
                projects.append({
                    "title": repo["name"],
                    "description": repo["description"] or "Без описания",
                    "link": repo["html_url"],
                })
    except requests.RequestException:
        pass

    return render_template(
        "portfolio_template.html",
        name=name,
        bio=bio,
        github=github,
        telegram=telegram,
        avatar=avatar,
        skills=skills,
        projects=projects,
        tool_icons=tool_icons,
    )


if __name__ == "__main__":
    create_table()
    app.run(debug=True)