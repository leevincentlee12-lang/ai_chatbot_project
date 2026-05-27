import unittest
from unittest.mock import patch

from app import app
from homework_helper import (
    answer_question,
    classify_math_request,
    evaluate_answer_details,
    factor_expression,
    generate_problem,
    generate_lesson,
    handle_math,
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

    def test_hard_practice_can_generate_factorable_quadratics(self):
        with patch("core.progression.random.choice", side_effect=lambda options: options[-1]):
            problem = generate_problem(level=3, user_id="hard-practice-test")

        self.assertEqual(problem["difficulty"], "Hard")
        self.assertEqual(problem["skill"], "quadratics")
        self.assertIn("x^2", problem["problem"])
        self.assertEqual(len(problem["solution"]), 2)

    def test_quadratic_practice_accepts_complete_solution_set(self):
        payload = evaluate_answer_details("x^2 - 5x + 6 = 0", "x = 2 or x = 3")
        self.assertEqual(payload["status"], "correct")
        self.assertIn("x = 2 or x = 3", payload["result"])

    def test_quadratic_practice_flags_missing_root(self):
        payload = evaluate_answer_details("x^2 - 5x + 6 = 0", "x = 2")
        self.assertEqual(payload["status"], "incorrect")
        self.assertIn("only part of the solution set", payload["details"])

    def test_learning_state_remembers_active_practice_problem(self):
        response = self.client.get("/practice/2")
        self.assertEqual(response.status_code, 200)
        problem_payload = response.get_json()

        state_response = self.client.get("/learning-state")
        self.assertEqual(state_response.status_code, 200)
        state = state_response.get_json()

        active_problem = state["active_practice_problem"]
        self.assertEqual(active_problem["problem"], problem_payload["problem"])
        self.assertEqual(active_problem["skill"], problem_payload["skill"])
        self.assertEqual(active_problem["difficulty"], problem_payload["difficulty"])
        self.assertEqual(active_problem["level"], 2)
        self.assertNotIn("solution", active_problem)

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

    def test_math_workflow_intent_dispatch_labels_core_requests(self):
        examples = {
            "solve 2x + 4 = 10": "solve_linear",
            "solve x^2 - 9 = 0": "solve_quadratic",
            "explain the discriminant in x^2 - 4x + 3 = 0": "explain_discriminant",
            "explain y = mx + c": "linear_graph_form",
            "factor x^2 - 9": "factor_expression",
            "simplify 2x + 3x - 4": "simplify_expression",
            "solve x+y=5 and x-y=1": "solve_simultaneous",
            "validate steps": "validate_steps",
            "practice problem": "generate_problem",
        }

        for question, expected_intent in examples.items():
            with self.subTest(question=question):
                match = classify_math_request(question)
                self.assertEqual(match.name, expected_intent)
                self.assertGreater(match.confidence, 0)

    def test_handle_math_simplifies_expression_through_intent_dispatch(self):
        result = handle_math("simplify 2x + 3x - 4")
        self.assertIn("Answer", result)
        self.assertIn("5*x - 4", result)

    def test_handle_math_solves_simultaneous_prompt_with_solve_prefix(self):
        result = handle_math("solve x+y=5 and x-y=1")
        self.assertIn("x = 3", result)
        self.assertIn("y = 2", result)

    def test_malformed_linear_equation_is_not_solved(self):
        result = handle_math("solve 2x + = 10")
        self.assertIn("could not read", result)
        self.assertNotIn("x = 5", result)

    def test_repeated_operator_equation_is_rejected_cleanly(self):
        result = handle_math("solve 2x ++ 4 = 10")
        self.assertIn("could not read", result)
        self.assertNotIn("x = 3", result)

    def test_explicit_multiplication_still_solves_via_symbolic_fallback(self):
        result = handle_math("solve 2*x + 4 = 10")
        self.assertIn("x = 3", result)

    def test_discriminant_explanation_works_in_main_answer_path(self):
        result = answer_question(
            "explain the discriminant in x^2 - 4x + 3 = 0",
            mode="step-by-step",
        )
        self.assertEqual(result["subject"], "Math")
        self.assertEqual(result["topic"], "Quadratic Equations")
        self.assertIn("The discriminant is 4", result["answer"])
        self.assertIn("b^2 - 4ac", result["answer"])
        self.assertNotIn("Provide an algebra equation", result["answer"])

    def test_linear_graph_form_explanation_works_in_main_answer_path(self):
        result = answer_question("explain y = mx + c", mode="step-by-step")
        self.assertEqual(result["subject"], "Math")
        self.assertEqual(result["topic"], "Linear Graphs")
        self.assertIn("m is the gradient", result["answer"])
        self.assertIn("c is the y-intercept", result["answer"])
        self.assertNotIn("Provide an algebra equation", result["answer"])

    def test_worded_linear_equation_prompts_extract_equation(self):
        examples = {
            "find x in 4x - 9 = 3": "x = 3",
            "what is x if 3x = 12": "x = 4",
            "solve for x: 2x + 4 = 10": "x = 3",
        }

        for question, expected in examples.items():
            with self.subTest(question=question):
                result = answer_question(question, mode="direct")
                self.assertEqual(result["subject"], "Math")
                self.assertEqual(result["answer"], expected)

    def test_malformed_step_validation_returns_educational_error(self):
        result = validate_steps([
            "2x + = 10",
            "x = 5",
        ])
        self.assertIn("Step 1 could not be read", result)
        self.assertIn("complete expression", result)

    def test_malformed_check_answer_request_returns_clean_error(self):
        payload = evaluate_answer_details("2x + = 10", "x = 5")
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["headline"], "Invalid Equation")
        self.assertIn("could not read", payload["details"])

    def test_main_answer_route_returns_clean_error_for_malformed_equation(self):
        result = answer_question("solve 2x + = 10", mode="direct")
        self.assertEqual(result["subject"], "Math")
        self.assertIn("could not read", result["answer"])
        self.assertNotIn("x = 5", result["answer"])

    def test_answer_question_allows_general_questions_with_algebra_nudge(self):
        result = answer_question("what caused WW2", mode="direct")
        self.assertEqual(result["subject"], "Humanities")
        self.assertEqual(result["topic"], "History and Geography")
        self.assertIn("WW2 was caused", result["answer"])
        self.assertIn("Algebra Focus", result["answer"])

    def test_what_can_you_do_gets_helpful_general_answer(self):
        result = answer_question("what can you do", mode="direct")
        self.assertEqual(result["subject"], "Unknown")
        self.assertIn("guided algebra learning platform", result["answer"])
        self.assertIn("Algebra Focus", result["answer"])

    def test_help_question_explains_platform_use(self):
        result = answer_question("how do I use this", mode="direct")
        self.assertEqual(result["subject"], "Unknown")
        self.assertIn("Use Direct for a final answer", result["answer"])
        self.assertIn("Practice Mode", result["answer"])
        self.assertIn("Try an algebra equation", result["followups"])

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

    def test_lesson_page_renders_dynamic_lesson_sections(self):
        response = self.client.get("/lessons/trigonometry")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Right-Angle Trigonometry", html)
        self.assertIn("Core Idea", html)
        self.assertIn("Key Points", html)
        self.assertIn("Worked Example", html)
        self.assertIn("Common Mistakes", html)
        self.assertIn("Practice Prompts", html)
        self.assertIn("find x if sin 35 = x/12", html)

    def test_learning_state_remembers_current_lesson(self):
        response = self.client.get("/lesson/trigonometry")
        self.assertEqual(response.status_code, 200)
        lesson_payload = response.get_json()

        state_response = self.client.get("/learning-state")
        self.assertEqual(state_response.status_code, 200)
        state = state_response.get_json()

        current_lesson = state["current_lesson"]
        self.assertEqual(current_lesson["topic"], lesson_payload["topic"])
        self.assertEqual(current_lesson["title"], "Right-Angle Trigonometry")
        self.assertIn("summary", current_lesson)

    def test_learning_state_exposes_recent_question_alias(self):
        response = self.client.post(
            "/ask",
            json={"question": "solve 2x + 4 = 10", "mode": "direct"},
        )
        self.assertEqual(response.status_code, 200)

        state_response = self.client.get("/learning-state")
        self.assertEqual(state_response.status_code, 200)
        state = state_response.get_json()

        self.assertEqual(state["recent_question"]["question"], "solve 2x + 4 = 10")
        self.assertTrue(state["recent_questions"])

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

    def test_homepage_links_to_practice_mode_without_embedded_practice_widget(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Open Practice Mode", html)
        self.assertIn('href="/practice"', html)
        self.assertNotIn("practice-easy", html)
        self.assertNotIn("practiceProblem", html)
        self.assertNotIn("studentAnswer", html)
        self.assertNotIn("submit-answer", html)

    def test_homepage_shows_external_feedback_form_link_when_configured(self):
        with patch.dict(
            "os.environ",
            {"FEEDBACK_FORM_URL": "https://docs.google.com/forms/d/e/example/formResponse"},
        ):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn(">Feedback</a>", html)
        self.assertIn("https://docs.google.com/forms/d/e/example/viewform", html)

    def test_feedback_form_link_is_available_in_secondary_page_nav(self):
        with patch.dict(
            "os.environ",
            {"FEEDBACK_FORM_URL": "https://docs.google.com/forms/d/e/example/viewform"},
        ):
            response = self.client.get("/practice")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn(">Feedback</a>", html)
        self.assertIn("https://docs.google.com/forms/d/e/example/viewform", html)

    def test_practice_mode_page_loads(self):
        response = self.client.get("/practice")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Practice Mode", html)
        self.assertIn("practiceModeAnswer", html)
        self.assertIn("x = 3 or x = -2", html)
        self.assertIn("practice.js", html)

    def test_progress_page_loads(self):
        response = self.client.get("/progress-page")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Student performance", html)
        self.assertIn("progressAccuracy", html)
        self.assertIn("skillScoreList", html)
        self.assertIn("recentActivityList", html)
        self.assertIn("progress.js", html)

    def test_about_page_loads_with_project_details(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Project Overview", html)
        self.assertIn("Technologies Used", html)
        self.assertIn("System Architecture", html)
        self.assertIn("User Input", html)
        self.assertIn("Subject Engine", html)
        self.assertIn("Feedback Generator", html)
        self.assertIn("Progress Tracking", html)
        self.assertIn("Deployment Details", html)
        self.assertIn("Future Improvements", html)

    def test_legacy_learn_route_still_loads_about_page(self):
        response = self.client.get("/learn")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Project Overview", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
