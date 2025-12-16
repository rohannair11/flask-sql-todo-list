from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "todo.db")

ALLOWED_PRIORITIES = {"Low", "Medium", "High"}


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
            priority TEXT NOT NULL CHECK(priority IN ('Low','Medium','High')),
            completed INTEGER NOT NULL CHECK(completed IN (0,1)),
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

        if (
            not title
            or not description
            or len(title) > 100
            or len(description) > 500
            or priority not in ALLOWED_PRIORITIES
        ):
            conn.close()
            return redirect(url_for("index"))

        created_at = datetime.now().strftime("%d %b %Y, %H:%M")

        cursor.execute("""
            INSERT INTO todos (title, description, priority, completed, created_at)
            VALUES (?, ?, ?, 0, ?)
        """, (title, description, priority, created_at))
        conn.commit()

    cursor.execute("""
        SELECT * FROM todos
        WHERE completed = 0
        ORDER BY id DESC
    """)
    todo_tasks = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM todos
        WHERE completed = 1
        ORDER BY id DESC
    """)
    done_tasks = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM todos")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 0")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM todos WHERE completed = 1")
    completed = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        todo_tasks=todo_tasks,
        done_tasks=done_tasks,
        total=total,
        pending=pending,
        completed=completed
    )


@app.route("/done/<int:todo_id>")
def mark_done(todo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET completed = 1 WHERE id = ?",
        (todo_id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/undo/<int:todo_id>")
def undo(todo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET completed = 0 WHERE id = ?",
        (todo_id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM todos WHERE id = ?",
        (todo_id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
