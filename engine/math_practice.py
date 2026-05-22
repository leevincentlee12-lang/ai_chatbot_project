"""Guided math practice session helpers."""

from core.parser import _extract_numeric_answer
from core.progression import generate_problem, guided_sessions


def guided_response(answer):
    """Evaluate a response inside the active guided-problem session."""
    if "solution" not in guided_sessions:
        return "Start a guided problem first."

    student_value = _extract_numeric_answer(answer)
    if student_value is None:
        return "Enter a numeric answer."

    correct = guided_sessions["solution"]
    if abs(student_value - correct) < 1e-9:
        guided_sessions.clear()
        return "Correct! You solved the equation."

    return "Not quite. Try isolating x before dividing."


def start_guided_problem():
    """Start a guided linear-equation problem."""
    problem_data = generate_problem(level=1)
    guided_sessions["problem"] = problem_data["problem"]
    guided_sessions["step"] = 1
    guided_sessions["solution"] = problem_data["solution"]

    constant = problem_data["problem"].split("+ (", 1)[1].split(")", 1)[0]
    return (
        f"Solve: {problem_data['problem']}\n"
        f"Step 1: subtract {constant} from both sides."
    )
