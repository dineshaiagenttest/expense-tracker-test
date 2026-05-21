import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

DATABASE_PATH = Path(__file__).parent.parent / "expense_tracker.db"


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title      TEXT    NOT NULL,
            amount     REAL    NOT NULL,
            category   TEXT    NOT NULL,
            date       TEXT    NOT NULL,
            notes      TEXT,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user


def create_user(name, email, password):
    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("An account with that email already exists.")
    finally:
        conn.close()


def seed_db():
    conn = get_db()

    conn.execute(
        "INSERT OR IGNORE INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Test User", "test@example.com", generate_password_hash("password123")),
    )

    user_id = conn.execute(
        "SELECT id FROM users WHERE email = 'test@example.com'"
    ).fetchone()["id"]

    already_seeded = conn.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()[0]

    if not already_seeded:
        sample_expenses = [
            (user_id, "Grocery run",         1250.00, "Food",          "2026-05-01", "Weekly groceries"),
            (user_id, "Metro card top-up",    500.00, "Travel",        "2026-05-05", None),
            (user_id, "Electricity bill",    1800.00, "Utilities",     "2026-05-10", "May bill"),
            (user_id, "Dinner with friends",  960.00, "Food",          "2026-05-14", "Restaurant outing"),
            (user_id, "Online course",       2499.00, "Education",     "2026-05-18", "Python bootcamp"),
            (user_id, "Doctor visit",         800.00, "Healthcare",    "2026-05-03", "General checkup"),
            (user_id, "Movie tickets",        450.00, "Entertainment", "2026-05-09", "Weekend outing"),
            (user_id, "Mobile recharge",      299.00, "Utilities",     "2026-05-15", None),
        ]

        conn.executemany(
            """
            INSERT INTO expenses (user_id, title, amount, category, date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            sample_expenses,
        )

    conn.commit()
    conn.close()
