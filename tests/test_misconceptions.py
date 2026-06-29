import unittest
import uuid

from core.misconceptions import detect_misconception
from homework_helper import evaluate_answer_details, get_learning_state


class MisconceptionEngineTests(unittest.TestCase):
    def test_detects_sign_error(self):
        result = detect_misconception("x = 5", "x = -5", "x = 5")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "SIGN_ERROR")

    def test_detects_forgot_to_divide(self):
        result = detect_misconception("3x = 12", "x = 12", "x = 4")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "FORGOT_TO_DIVIDE")

    def test_detects_reversed_division(self):
        result = detect_misconception("4x = 20", "x = 4/20", "x = 5")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "REVERSED_DIVISION")

    def test_detects_distributive_error(self):
        result = detect_misconception("3(x + 4) = 21", "x = 17/3", "x = 3")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "DISTRIBUTIVE_ERROR")

    def test_detects_combining_unlike_terms(self):
        result = detect_misconception("simplify 2x + 3", "5x", "2x + 3")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "COMBINING_UNLIKE_TERMS")

    def test_returns_none_when_no_clear_misconception_exists(self):
        result = detect_misconception("2x + 4 = 10", "x = 100", "x = 3")

        self.assertIsNone(result)

    def test_answer_check_records_misconception_counts(self):
        user_id = f"misconception-test-{uuid.uuid4().hex}"

        first = evaluate_answer_details("3x = 12", "x = 12", user_id=user_id)
        second = evaluate_answer_details("3x = 12", "x = 12", user_id=user_id)
        state = get_learning_state(user_id=user_id)

        self.assertEqual(first["misconception"]["id"], "FORGOT_TO_DIVIDE")
        self.assertEqual(second["misconception"]["count"], 2)
        self.assertEqual(state["misconceptions"]["FORGOT_TO_DIVIDE"], 2)
        self.assertEqual(
            state["most_common_misconception"]["id"],
            "FORGOT_TO_DIVIDE",
        )
        self.assertEqual(
            state["misconception_recommendations"][0]["id"],
            "FORGOT_TO_DIVIDE",
        )
        self.assertIn("Misconception Detected", second["details"])


if __name__ == "__main__":
    unittest.main()
