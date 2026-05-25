"""Guided math practice session helpers."""

from core.parser import _extract_numeric_answer
from core.progression import (
    clear_guided_session,
    generate_problem,
    get_guided_session,
    set_guided_session,
)


def guided_response(answer, user_id=None):
    """Evaluate a response inside the active guided-problem session."""
    session = get_guided_session(user_id)
    if "solution" not in session:
        return "Start a guided problem first."

    student_value = _extract_numeric_answer(answer)
    if student_value is None:
        return "Enter a numeric answer."

    correct = session["solution"]
    if abs(student_value - correct) < 1e-9:
        clear_guided_session(user_id)
        return "Correct! You solved the equation."

    return "Not quite. Try isolating x before dividing."


def start_guided_problem(user_id=None):
    """Start a guided linear-equation problem."""
    problem_data = generate_problem(level=1, user_id=user_id)
    set_guided_session(
        problem_data["problem"],
        step=1,
        solution=problem_data["solution"],
        user_id=user_id,
    )

    constant = problem_data["problem"].split("+ (", 1)[1].split(")", 1)[0]
    return (
        f"Solve: {problem_data['problem']}\n"
        f"Step 1: subtract {constant} from both sides."
    )
