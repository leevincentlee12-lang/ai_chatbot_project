import unittest

from app import app
from homework_helper import (
    answer_question,
    evaluate_answer_details,
    factor_expression,
    generate_lesson,
    list_lessons,
    validate_steps,
)


class HomeworkHelperAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.testing = True
        cls.client = app.test_client()

    def test_answer_question_requires_mode_when_unclear(self):
        result = answer_question("solve x^2 - 9 = 0")
        self.assertEqual(result["subject"], "Math")
        self.assertEqual(
            result["answer"],
            "Which mode should I use: Direct, Step-by-step, or Hint?",
        )

    def test_answer_question_handles_caret_input_in_step_mode(self):
        result = answer_question("solve x^2 - 9 = 0", mode="step-by-step")
        self.assertEqual(result["subject"], "Math")
        self.assertIn("1.", result["answer"])
        self.assertIn("x = -3 or x = 3", result["answer"])

    def test_practice_endpoint_returns_public_problem_shape(self):
        response = self.client.get("/practice/2")
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertIn("problem", payload)
        self.assertIn("difficulty", payload)
        self.assertIn("skill", payload)
        self.assertNotIn("solution", payload)

    def test_check_answer_accepts_assignment_format(self):
        response = self.client.post(
            "/check-answer",
            json={"equation": "2x + 4 = 10", "answer": "x = 3"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "correct")
        self.assertIn("Correct", payload["result"])
        self.assertIn("Why It Works", payload["details"])

    def test_validate_steps_flags_invalid_transformation(self):
        result = validate_steps([
            "3x + 4 = 19",
            "3x = 19 + 4",
        ])
        self.assertIn("Transformation error", result)

    def test_factoring_returns_factored_form(self):
        result = factor_expression("x^2 - 9")
        self.assertIn("(x - 3)*(x + 3)", result)

    def test_answer_question_restricts_non_algebra_scope(self):
        result = answer_question("what caused WW2", mode="direct")
        self.assertEqual(result["subject"], "Restricted")
        self.assertEqual(
            result["answer"],
            "This system is restricted to algebra questions for this experiment.",
        )

    def test_direct_mode_returns_final_answer_only(self):
        result = answer_question("solve 2x + 4 = 10", mode="direct")
        self.assertEqual(result["answer"], "x = 3")
        self.assertEqual(result["followups"], [])

    def test_natural_step_request_is_detected_without_mode_field(self):
        result = answer_question("show the full working for 2x + 4 = 10")
        self.assertIn("1.", result["answer"])
        self.assertIn("x = 3", result["answer"])

    def test_hint_mode_returns_single_hint_without_solution(self):
        result = answer_question("solve 2x + 4 = 10", mode="hint")
        self.assertIn("same operation", result["answer"])
        self.assertNotIn("x = 3", result["answer"])

    def test_incorrect_answer_feedback_is_diagnostic(self):
        payload = evaluate_answer_details("3x + 6 = 15", "9")
        self.assertEqual(payload["status"], "incorrect")
        self.assertIn("Likely Issue", payload["details"])
        self.assertIn("did not divide by its coefficient", payload["details"])

    def test_lesson_catalog_includes_trigonometry(self):
        lessons = list_lessons()
        self.assertTrue(any(lesson["topic"] == "trigonometry" for lesson in lessons))

    def test_generate_lesson_returns_rich_payload(self):
        lesson = generate_lesson("trigonometry")
        self.assertEqual(lesson["title"], "Right-Angle Trigonometry")
        self.assertTrue(len(lesson["common_mistakes"]) >= 2)
        self.assertTrue(len(lesson["practice_prompts"]) >= 2)
        self.assertIn("Worked Example", lesson["display_text"])

    def test_lessons_endpoint_returns_catalog(self):
        response = self.client.get("/lessons")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("lessons", payload)
        self.assertTrue(any(lesson["topic"] == "trigonometry" for lesson in payload["lessons"]))

    def test_ratio_question_is_supported(self):
        result = answer_question("simplify the ratio 6:9", mode="step-by-step")
        self.assertEqual(result["topic"], "Ratios")
        self.assertIn("2:3", result["answer"])

    def test_ask_endpoint_accepts_explicit_mode(self):
        response = self.client.post(
            "/ask",
            json={"question": "solve 2x + 4 = 10", "mode": "direct"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["answer"], "x = 3")


if __name__ == "__main__":
    unittest.main()
