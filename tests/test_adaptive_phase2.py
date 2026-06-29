import unittest
import uuid

from homework_helper import (
    adjust_skill,
    answer_question,
    build_teacher_snapshot,
    evaluate_answer_details,
    generate_adaptive_problem,
    get_learning_state,
)


class AdaptivePhase2Tests(unittest.TestCase):
    def test_mastery_updates_and_repeated_misconception_penalty(self):
        user_id = f"phase2-mastery-{uuid.uuid4().hex}"
        adjust_skill("linear_equations", score_delta=50, user_id=user_id)

        correct = evaluate_answer_details("3x = 12", "x = 4", user_id=user_id)
        first_wrong = evaluate_answer_details("3x = 12", "x = 12", user_id=user_id)
        second_wrong = evaluate_answer_details("3x = 12", "x = 12", user_id=user_id)
        state = get_learning_state(user_id=user_id)

        self.assertEqual(correct["status"], "correct")
        self.assertEqual(first_wrong["misconception"]["id"], "FORGOT_TO_DIVIDE")
        self.assertEqual(second_wrong["misconception"]["count"], 2)
        self.assertEqual(
            state["skill_progression"]["linear_equations"]["score"],
            45,
        )
        self.assertEqual(
            state["misconceptions"]["FORGOT_TO_DIVIDE"],
            2,
        )

    def test_recommendation_prioritises_repeated_misconception(self):
        user_id = f"phase2-recommendation-{uuid.uuid4().hex}"

        evaluate_answer_details("3(x + 4) = 21", "x = 17/3", user_id=user_id)
        evaluate_answer_details("3(x + 4) = 21", "x = 17/3", user_id=user_id)
        state = get_learning_state(user_id=user_id)

        self.assertEqual(state["recommendation"]["skill"], "expanding_brackets")
        self.assertIn("Repeated distributive law error", state["recommendation"]["reason"])
        self.assertEqual(
            state["dashboard"]["current_focus_area"],
            "Expanding Brackets",
        )

    def test_adaptive_question_selection_uses_focus_area(self):
        user_id = f"phase2-selection-{uuid.uuid4().hex}"

        evaluate_answer_details("3(x + 4) = 21", "x = 17/3", user_id=user_id)
        evaluate_answer_details("3(x + 4) = 21", "x = 17/3", user_id=user_id)
        problem = generate_adaptive_problem(user_id=user_id, requested_level=3)
        state = get_learning_state(user_id=user_id)

        self.assertEqual(problem["skill"], "expanding_brackets")
        self.assertIn("(", problem["problem"])
        self.assertIn("Repeated distributive law error", problem["adaptive_reason"])
        self.assertEqual(state["recent_question"]["question"], problem["problem"])

    def test_new_student_starts_with_linear_equations(self):
        user_id = f"phase2-new-student-{uuid.uuid4().hex}"

        problem = generate_adaptive_problem(user_id=user_id, requested_level=3)

        self.assertEqual(problem["skill"], "linear_equations")
        self.assertEqual(problem["adaptive_focus"], "Linear Equations")

    def test_dashboard_tracks_history_hint_usage_and_recommendation(self):
        user_id = f"phase2-dashboard-{uuid.uuid4().hex}"

        answer_question("solve 2x + 4 = 10", mode="hint", user_id=user_id)
        evaluate_answer_details("2x + 4 = 10", "x = 3", user_id=user_id)
        state = get_learning_state(user_id=user_id)

        self.assertGreaterEqual(state["dashboard"]["hint_usage"], 1)
        self.assertGreaterEqual(state["overall_mastery"], 0)
        self.assertTrue(state["mastery_history"])
        self.assertTrue(state["learning_events"])
        self.assertIn("recommended_next_topic", state["dashboard"])

    def test_teacher_snapshot_uses_existing_learning_state(self):
        user_id = f"phase2-teacher-{uuid.uuid4().hex}"

        evaluate_answer_details("2x + 4 = 10", "x = 3", user_id=user_id)
        state = get_learning_state(user_id=user_id)
        snapshot = build_teacher_snapshot(user_id, state)

        self.assertEqual(snapshot["user_id"], user_id)
        self.assertIn("mastery_by_topic", snapshot)
        self.assertIn("misconceptions", snapshot)
        self.assertIn("recent_activity", snapshot)

    def test_adaptive_hint_mentions_repeated_sign_errors(self):
        user_id = f"phase2-hint-{uuid.uuid4().hex}"

        evaluate_answer_details("x = 5", "x = -5", user_id=user_id)
        evaluate_answer_details("x = 5", "x = -5", user_id=user_id)
        result = answer_question("solve x = 5", mode="hint", user_id=user_id)

        self.assertEqual(result["subject"], "Math")
        self.assertIn("recently made several sign errors", result["answer"])
        self.assertNotIn("x = 5", result["answer"])


if __name__ == "__main__":
    unittest.main()
