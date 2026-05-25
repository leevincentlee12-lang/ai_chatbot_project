import json
import os
import tempfile
import traceback
import uuid
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.parse

from flask import Flask, jsonify, render_template, request, session

from core.session_memory import (
    get_session_memory,
    remember_active_practice_problem,
    remember_current_lesson,
)
from homework_helper import (
    answer_question,
    evaluate_answer_details,
    generate_lesson,
    generate_problem,
    get_learning_state,
    get_student_skills,
    get_student_stats,
    list_lessons,
    record_lesson_completed,
    validate_steps,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-only-homework-helper-secret",
)

BASE_DIR = Path(__file__).resolve().parent
FEEDBACK_LOG_PATH = BASE_DIR / "feedback_log.json"
FEEDBACK_CONFIG_PATH = BASE_DIR / "feedback_config.json"

# Maximum number of feedback entries retained in the log file.
# Oldest entries are dropped once this limit is reached.
FEEDBACK_MAX_ENTRIES = 10_000

# Module-level cache for the Google Forms forwarding config.
# Loaded once on first use; set to _UNLOADED sentinel until then.
_UNLOADED = object()
_feedback_config_cache = _UNLOADED


def _json_payload():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else {}


def _current_user_id():
    """Return the anonymous browser user id stored in the Flask session."""
    if "user_id" not in session:
        session["user_id"] = uuid.uuid4().hex
    return session["user_id"]


def _learning_state_payload():
    """Return persistent learning state plus lightweight session memory."""
    state = get_learning_state(user_id=_current_user_id())
    state.update(get_session_memory(session))
    return state


def _load_feedback_logs():
    try:
        with FEEDBACK_LOG_PATH.open("r", encoding="utf-8") as file:
            logs = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    return logs if isinstance(logs, list) else []


def _save_feedback_logs(logs):
    """Write feedback logs atomically to avoid truncation on failure."""
    dir_path = FEEDBACK_LOG_PATH.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            json.dump(logs, tmp_file, indent=2)
        os.replace(tmp_path, FEEDBACK_LOG_PATH)
    except Exception:
        # Clean up the temp file if the write or rename failed.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _load_feedback_config():
    """Return the Google Forms forwarding config, cached after first load."""
    global _feedback_config_cache
    if _feedback_config_cache is not _UNLOADED:
        return _feedback_config_cache

    try:
        with FEEDBACK_CONFIG_PATH.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
            result = cfg if isinstance(cfg, dict) else None
    except (FileNotFoundError, json.JSONDecodeError):
        result = None

    _feedback_config_cache = result
    return result


def _forward_feedback_to_google(record):
    cfg = _load_feedback_config()
    if not cfg:
        return False

    form_url = cfg.get("form_url")
    mappings = cfg.get("mappings", {})
    if not form_url or not isinstance(mappings, dict):
        return False

    form_data = {}
    for local_key, entry_name in mappings.items():
        value = record.get(local_key)
        # Skip None values — do not send the string "None" to Google Forms.
        if value is None:
            continue
        try:
            str_value = str(value).strip()
        except Exception:
            str_value = ""
        if str_value:
            form_data[entry_name] = str_value

    if not form_data:
        return False

    try:
        data = urllib.parse.urlencode(form_data).encode("utf-8")
        req = urllib.request.Request(
            form_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode() in (200, 302)
    except Exception:
        traceback.print_exc()
        return False


@app.errorhandler(Exception)
def handle_exception(error):
    print("SERVER ERROR:")
    traceback.print_exc()

    return jsonify({
        "answer": "Server error occurred. Please try again.",
        "subject": "System",
        "topic": "Backend error",
        "followups": [],
    }), 500


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = _json_payload()
    question = str(data.get("question", "")).strip()
    mode = str(data.get("mode", "")).strip()

    if not question:
        return jsonify({
            "answer": "Please enter a question.",
            "subject": "Unknown",
            "topic": "General Study Help",
            "followups": [],
        }), 400

    result = answer_question(question, mode=mode, user_id=_current_user_id())
    return jsonify(result)


@app.route("/validate", methods=["POST"])
def validate():
    data = _json_payload()
    raw_steps = data.get("steps", [])

    if not isinstance(raw_steps, list):
        return jsonify({"result": "Steps must be provided as a list."}), 400

    steps = [str(step) for step in raw_steps]
    return jsonify({"result": validate_steps(steps)})


@app.route("/feedback", methods=["POST"])
def feedback():
    data = _json_payload()
    rating = str(data.get("rating", "")).strip()

    if rating and rating not in {"1", "2", "3", "4", "5"}:
        return jsonify({"status": "invalid rating"}), 400

    # Enforce a maximum comment length to prevent unbounded log growth.
    comment_raw = data.get("comment", "")
    comment = str(comment_raw).strip()[:2000] if comment_raw is not None else ""

    record = {
        "question": str(data.get("question", "")).strip() or None,
        "subject": str(data.get("subject", "")).strip() or "Unknown",
        "topic": str(data.get("topic", "")).strip() or "General",
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.now().isoformat(),
    }

    logs = _load_feedback_logs()
    logs.append(record)

    # Trim to the configured maximum to prevent unbounded file growth.
    if len(logs) > FEEDBACK_MAX_ENTRIES:
        logs = logs[-FEEDBACK_MAX_ENTRIES:]

    _save_feedback_logs(logs)

    # Attempt to forward to Google Form if configured.
    forwarded = _forward_feedback_to_google(record)

    return jsonify({"status": "saved", "forwarded": forwarded})


@app.route("/learn")
def learn():
    return render_template("about.html")


@app.route("/practice")
def practice_mode():
    return render_template("practice.html")


@app.route("/progress-page")
def progress_page():
    return render_template("progress.html")


@app.route("/analytics")
def analytics():
    logs = _load_feedback_logs()
    ratings = [
        int(log["rating"])
        for log in logs
        if str(log.get("rating", "")).isdigit()
    ]

    subject_counts = {}
    for log in logs:
        subject = log.get("subject", "Unknown") or "Unknown"
        subject_counts[subject] = subject_counts.get(subject, 0) + 1

    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0

    return jsonify({
        "total_questions": len(logs),
        "average_rating": average_rating,
        "subject_distribution": subject_counts,
    })


@app.route("/practice/<int:level>")
def practice(level):
    problem = generate_problem(level, user_id=_current_user_id())
    remember_active_practice_problem(session, problem, level=level)
    return jsonify({
        "skill": problem["skill"],
        "problem": problem["problem"],
        "difficulty": problem["difficulty"],
    })


@app.route("/lesson/<topic>")
def lesson(topic):
    record_lesson_completed(user_id=_current_user_id())
    lesson_data = generate_lesson(topic)
    remember_current_lesson(session, lesson_data)
    return jsonify(lesson_data)


@app.route("/lessons/<topic>")
def lesson_page(topic):
    record_lesson_completed(user_id=_current_user_id())
    lesson_data = generate_lesson(topic)
    remember_current_lesson(session, lesson_data)
    return render_template(
        "lesson.html",
        lesson=lesson_data,
        lessons=list_lessons(),
    )


@app.route("/lessons")
def lessons():
    return jsonify({"lessons": list_lessons()})


@app.route("/skills")
def skills():
    return jsonify(get_student_skills(user_id=_current_user_id()))


@app.route("/progress")
def progress():
    stats = get_student_stats(user_id=_current_user_id())
    attempted = stats["problems_attempted"]
    accuracy = round(
        stats["correct_answers"] / attempted * 100,
        2,
    ) if attempted else 0

    return jsonify({
        "questions_asked": stats["questions_asked"],
        "attempted": attempted,
        "correct": stats["correct_answers"],
        "accuracy": accuracy,
        "lessons_completed": stats["lessons_completed"],
    })


@app.route("/learning-state")
def learning_state():
    return jsonify(_learning_state_payload())


@app.route("/check-answer", methods=["POST"])
def check_answer():
    data = _json_payload()
    equation = str(data.get("equation", "")).strip()
    answer = str(data.get("answer", "")).strip()

    if not equation:
        return jsonify({"result": "No equation provided."}), 400

    if not answer:
        return jsonify({"result": "No answer provided."}), 400

    result = evaluate_answer_details(
        equation,
        answer,
        user_id=_current_user_id(),
    )
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
