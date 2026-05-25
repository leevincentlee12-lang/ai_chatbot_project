import unittest
import uuid

from homework_helper import (
    answer_question,
    evaluate_answer_details,
    get_learning_state,
    get_student_stats,
)


class AdaptiveStateTests(unittest.TestCase):
    def test_progress_is_isolated_by_user_id(self):
        user_one = f"test-{uuid.uuid4().hex}"
        user_two = f"test-{uuid.uuid4().hex}"

        answer_question("solve 2x + 4 = 10", mode="direct", user_id=user_one)
        evaluate_answer_details("2x + 4 = 10", "x = 3", user_id=user_one)

        one_stats = get_student_stats(user_id=user_one)
        two_stats = get_student_stats(user_id=user_two)

        self.assertEqual(one_stats["questions_asked"], 1)
        self.assertEqual(one_stats["problems_attempted"], 1)
        self.assertEqual(one_stats["correct_answers"], 1)
        self.assertEqual(two_stats["questions_asked"], 0)
        self.assertEqual(two_stats["problems_attempted"], 0)
        self.assertEqual(two_stats["correct_answers"], 0)

    def test_learning_state_tracks_recent_questions_and_mistakes(self):
        user_id = f"test-{uuid.uuid4().hex}"

        answer_question("solve 2x + 4 = 10", mode="direct", user_id=user_id)
        evaluate_answer_details("2x + 4 = 10", "x = 2", user_id=user_id)

        state = get_learning_state(user_id=user_id)

        self.assertEqual(state["current_topic"], "Linear Equations")
        self.assertEqual(
            state["recent_question"]["question"],
            "solve 2x + 4 = 10",
        )
        self.assertTrue(state["recent_questions"])
        self.assertEqual(state["mistake_history"][0]["skill"], "linear_equations")
        self.assertEqual(state["recent_mistakes"][0]["skill"], "linear_equations")
        self.assertIn("skill_progression", state)


if __name__ == "__main__":
    unittest.main()
