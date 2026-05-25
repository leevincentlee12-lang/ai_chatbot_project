"""SQLite-backed user state for adaptive tutoring.

This module is the persistence boundary for session memory. Flask should store
only a small user id in the browser session; this store keeps the actual
learning state on the server side.
"""

import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_USER_ID = "default"
MAX_RECENT_QUESTIONS = 20
MAX_MISTAKES = 50

DEFAULT_STATS = {
    "questions_asked": 0,
    "problems_attempted": 0,
    "correct_answers": 0,
    "lessons_completed": 0,
}

DEFAULT_SKILLS = {
    "linear_equations": {"score": 0, "attempts": 0},
    "quadratics": {"score": 0, "attempts": 0},
    "factoring": {"score": 0, "attempts": 0},
    "fractions": {"score": 0, "attempts": 0},
    "indices": {"score": 0, "attempts": 0},
}

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "instance" / "homework_helper.sqlite3"

_INIT_LOCK = threading.RLock()
_INITIALIZED = False


def _now():
    return datetime.now(timezone.utc).isoformat()


def _normalise_user_id(user_id):
    value = str(user_id or DEFAULT_USER_ID).strip()
    return value if value else DEFAULT_USER_ID


def get_db_path():
    configured = os.environ.get("HOMEWORK_HELPER_DB_PATH")
    return Path(configured).expanduser() if configured else DEFAULT_DB_PATH


def _connect():
    initialize_store()
    conn = sqlite3.connect(str(get_db_path()), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _connect_without_init():
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_store():
    global _INITIALIZED
    if _INITIALIZED:
        return

    with _INIT_LOCK:
        if _INITIALIZED:
            return

        with _connect_without_init() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    current_topic TEXT NOT NULL DEFAULT 'linear_equations',
                    difficulty INTEGER NOT NULL DEFAULT 1,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    correct_streak INTEGER NOT NULL DEFAULT 0,
                    last_question_ts REAL
                );

                CREATE TABLE IF NOT EXISTS stats (
                    user_id TEXT PRIMARY KEY,
                    questions_asked INTEGER NOT NULL DEFAULT 0,
                    problems_attempted INTEGER NOT NULL DEFAULT 0,
                    correct_answers INTEGER NOT NULL DEFAULT 0,
                    lessons_completed INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS skills (
                    user_id TEXT NOT NULL,
                    skill TEXT NOT NULL,
                    score INTEGER NOT NULL DEFAULT 0,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, skill),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS recent_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    subject TEXT,
                    topic TEXT,
                    mode TEXT,
                    asked_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS mistakes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    skill TEXT,
                    question TEXT,
                    submitted_answer TEXT,
                    correct_answer TEXT,
                    issue TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS step_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    step_text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS guided_sessions (
                    user_id TEXT PRIMARY KEY,
                    problem TEXT NOT NULL,
                    step INTEGER NOT NULL,
                    solution REAL NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                        ON DELETE CASCADE
                );
                """
            )
        _INITIALIZED = True


def ensure_user(user_id=None):
    user_id = _normalise_user_id(user_id)
    created = _now()

    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id, created_at, updated_at)
            VALUES (?, ?, ?)
            """,
            (user_id, created, created),
        )
        conn.execute(
            "INSERT OR IGNORE INTO stats (user_id) VALUES (?)",
            (user_id,),
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO skills (user_id, skill, score, attempts)
            VALUES (?, ?, ?, ?)
            """,
            [
                (user_id, skill, data["score"], data["attempts"])
                for skill, data in DEFAULT_SKILLS.items()
            ],
        )
    return user_id


def get_stats(user_id=None):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM stats WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return {key: int(row[key]) for key in DEFAULT_STATS}


def increment_stat(user_id, stat_name, amount=1):
    if stat_name not in DEFAULT_STATS:
        raise ValueError(f"Unknown stat: {stat_name}")

    user_id = ensure_user(user_id)
    with _connect() as conn:
        conn.execute(
            f"UPDATE stats SET {stat_name} = {stat_name} + ? WHERE user_id = ?",
            (int(amount), user_id),
        )


def get_skills(user_id=None):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT skill, score, attempts
            FROM skills
            WHERE user_id = ?
            ORDER BY skill
            """,
            (user_id,),
        ).fetchall()

    return {
        row["skill"]: {
            "score": int(row["score"]),
            "attempts": int(row["attempts"]),
        }
        for row in rows
    }


def get_or_create_skill(user_id, skill):
    user_id = ensure_user(user_id)
    skill = str(skill or "linear_equations").strip() or "linear_equations"

    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO skills (user_id, skill, score, attempts)
            VALUES (?, ?, 0, 0)
            """,
            (user_id, skill),
        )
        row = conn.execute(
            """
            SELECT skill, score, attempts
            FROM skills
            WHERE user_id = ? AND skill = ?
            """,
            (user_id, skill),
        ).fetchone()

    return {
        "score": int(row["score"]),
        "attempts": int(row["attempts"]),
    }


def set_skill(user_id, skill, score, attempts):
    user_id = ensure_user(user_id)
    skill = str(skill or "linear_equations").strip() or "linear_equations"
    score = max(0, min(100, int(score)))
    attempts = max(0, int(attempts))

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO skills (user_id, skill, score, attempts)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, skill)
            DO UPDATE SET score = excluded.score,
                          attempts = excluded.attempts
            """,
            (user_id, skill, score, attempts),
        )

    return {"score": score, "attempts": attempts}


def adjust_skill(user_id, skill, score_delta=0, attempt_delta=0):
    current = get_or_create_skill(user_id, skill)
    return set_skill(
        user_id,
        skill,
        current["score"] + int(score_delta),
        current["attempts"] + int(attempt_delta),
    )


def get_profile(user_id=None):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT current_topic, difficulty, attempts, correct_streak,
                   last_question_ts
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    return {
        "skills": get_skills(user_id),
        "current_topic": row["current_topic"],
        "difficulty": int(row["difficulty"]),
        "attempts": int(row["attempts"]),
        "correct_streak": int(row["correct_streak"]),
        "last_question_ts": row["last_question_ts"],
    }


def update_profile(user_id=None, **fields):
    allowed = {
        "current_topic",
        "difficulty",
        "attempts",
        "correct_streak",
        "last_question_ts",
    }
    clean_fields = {key: value for key, value in fields.items() if key in allowed}
    if not clean_fields:
        return get_profile(user_id)

    user_id = ensure_user(user_id)
    clean_fields["updated_at"] = _now()
    assignments = ", ".join(f"{key} = ?" for key in clean_fields)
    values = list(clean_fields.values()) + [user_id]

    with _connect() as conn:
        conn.execute(
            f"UPDATE users SET {assignments} WHERE user_id = ?",
            values,
        )

    return get_profile(user_id)


def add_recent_question(user_id, question, subject=None, topic=None, mode=None):
    user_id = ensure_user(user_id)
    text = str(question or "").strip()
    if not text:
        return

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO recent_questions (
                user_id, question, subject, topic, mode, asked_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, text, subject, topic, mode, _now()),
        )
        ids_to_delete = conn.execute(
            """
            SELECT id
            FROM recent_questions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT -1 OFFSET ?
            """,
            (user_id, MAX_RECENT_QUESTIONS),
        ).fetchall()
        if ids_to_delete:
            conn.executemany(
                "DELETE FROM recent_questions WHERE id = ?",
                [(row["id"],) for row in ids_to_delete],
            )


def get_recent_questions(user_id=None, limit=10):
    user_id = ensure_user(user_id)
    limit = max(1, min(MAX_RECENT_QUESTIONS, int(limit)))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT question, subject, topic, mode, asked_at
            FROM recent_questions
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    return [
        {
            "question": row["question"],
            "subject": row["subject"],
            "topic": row["topic"],
            "mode": row["mode"],
            "asked_at": row["asked_at"],
        }
        for row in rows
    ]


def add_mistake(
    user_id,
    skill=None,
    question=None,
    submitted_answer=None,
    correct_answer=None,
    issue=None,
):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO mistakes (
                user_id, skill, question, submitted_answer, correct_answer,
                issue, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                skill,
                question,
                submitted_answer,
                correct_answer,
                issue,
                _now(),
            ),
        )
        ids_to_delete = conn.execute(
            """
            SELECT id
            FROM mistakes
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT -1 OFFSET ?
            """,
            (user_id, MAX_MISTAKES),
        ).fetchall()
        if ids_to_delete:
            conn.executemany(
                "DELETE FROM mistakes WHERE id = ?",
                [(row["id"],) for row in ids_to_delete],
            )


def get_mistakes(user_id=None, limit=10):
    user_id = ensure_user(user_id)
    limit = max(1, min(MAX_MISTAKES, int(limit)))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT skill, question, submitted_answer, correct_answer, issue,
                   created_at
            FROM mistakes
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    return [
        {
            "skill": row["skill"],
            "question": row["question"],
            "submitted_answer": row["submitted_answer"],
            "correct_answer": row["correct_answer"],
            "issue": row["issue"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def get_steps(user_id=None):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT step_text
            FROM step_history
            WHERE user_id = ?
            ORDER BY id
            """,
            (user_id,),
        ).fetchall()
    return [row["step_text"] for row in rows]


def append_step(user_id, step_text):
    user_id = ensure_user(user_id)
    step_text = str(step_text or "").strip()
    if not step_text:
        return len(get_steps(user_id))

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO step_history (user_id, step_text, created_at)
            VALUES (?, ?, ?)
            """,
            (user_id, step_text, _now()),
        )
        count = conn.execute(
            "SELECT COUNT(*) AS total FROM step_history WHERE user_id = ?",
            (user_id,),
        ).fetchone()["total"]
    return int(count)


def clear_steps(user_id=None):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        conn.execute(
            "DELETE FROM step_history WHERE user_id = ?",
            (user_id,),
        )


def get_guided_session(user_id=None):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT problem, step, solution
            FROM guided_sessions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return {}

    return {
        "problem": row["problem"],
        "step": int(row["step"]),
        "solution": float(row["solution"]),
    }


def set_guided_session(user_id, problem, step, solution):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO guided_sessions (
                user_id, problem, step, solution, updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET problem = excluded.problem,
                          step = excluded.step,
                          solution = excluded.solution,
                          updated_at = excluded.updated_at
            """,
            (user_id, problem, int(step), float(solution), _now()),
        )


def clear_guided_session(user_id=None):
    user_id = ensure_user(user_id)
    with _connect() as conn:
        conn.execute(
            "DELETE FROM guided_sessions WHERE user_id = ?",
            (user_id,),
        )
