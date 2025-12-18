from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "todo.db")


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")

        if not title or not description:
            conn.close()
            return redirect(url_for("index"))

        created_at = datetime.now().strftime("%d %b %Y, %H:%M")

        cursor.execute("""
            INSERT INTO todos (title, description, priority, created_at)
            VALUES (?, ?, ?, ?)
        """, (title, description, priority, created_at))
        conn.commit()

    cursor.execute("SELECT * FROM todos ORDER BY id DESC")
    tasks = cursor.fetchall()
    conn.close()

    return render_template("index.html", tasks=tasks)


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")

        if not title or not description:
            conn.close()
            return redirect(url_for("edit", task_id=task_id))

        cursor.execute("""
            UPDATE todos
            SET title = ?, description = ?, priority = ?
            WHERE id = ?
        """, (title, description, priority, task_id))

        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    cursor.execute("SELECT * FROM todos WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()

    return render_template("edit.html", task=task)


@app.route("/delete/<int:task_id>")
def delete(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
