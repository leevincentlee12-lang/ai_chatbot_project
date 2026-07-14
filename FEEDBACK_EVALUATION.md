# Feedback Evaluation

## Purpose

This document summarises feedback collected from a mathematics teacher and
student testers, then links that feedback to specific improvements made in the
Adaptive Algebra Learning Platform.

The aim is not to claim the platform is better than general AI tools. The aim
is to show an iterative engineering process: build, test, identify weaknesses,
improve, and verify.

## Feedback Sources

| Source | Evidence Type | What It Shows |
| --- | --- | --- |
| Mathematics teacher | Written feedback and reference letter | Mathematical reasoning, clarity of explanations, educational purpose, and suggested improvements |
| Student testers | Feedback form responses and informal feedback | Usability, confusion points, practice difficulty, and requested learning features |
| Automated tests | Regression test suite | Core workflows continue to work after changes |
| Screenshots | Application and before/after images | Visible evidence of product improvements |

Note: teacher contact details and private reference material should be used in
application submissions only, not published publicly in the GitHub README.

## Teacher Feedback Summary

The mathematics teacher feedback was positive overall. The key points were:

- the mathematical reasoning appeared accurate
- examples followed appropriate algebraic methods
- explanations were clear and easy to follow
- Step-by-step Mode was especially clear
- Hint Mode was useful because it encourages independent thinking
- the platform could support revision, homework, and independent practice

The teacher also suggested improvements:

- add feedback for common mistakes
- add more visual representations, such as graphs
- include a wider variety of question difficulties

## Student Feedback Summary

Student testers generally found the platform clear and usable. The most common
positive comments were:

- the website looked professional
- responses were mostly understandable
- step feedback was useful
- learning prompts and explanations helped guide practice
- the concept was strong overall

The main improvement points were:

- practice questions were too similar and too easy at the highest difficulty
- students wanted space to show working before entering a final answer
- default mode selection was confusing
- students wanted easier answer entry and clearer layout
- the text could feel cluttered
- the platform needed better handling for tutorial-style questions and hints

## Improvements Made From Feedback

| Feedback | Change Made | Evidence |
| --- | --- | --- |
| Hard practice questions were too easy and repetitive | Added harder algebra, rational equations, graph-feature practice, and coordinate geometry practice | `improvement_before_after_images/02_harder_practice_before_after.png` |
| Students wanted working-out space | Added Practice Mode working space and working validation | `improvement_before_after_images/03_working_space_before_after.png` |
| Default mode was confusing | Made Step-by-step Mode the default | Homepage and Practice Mode screenshots |
| Text felt cluttered | Improved educational response formatting into Answer, Method, Why, Check, and Next Step sections | `application_screenshots/02_step_by_step_solution.png` |
| Teacher suggested common mistake feedback | Added rule-based misconception detection and targeted feedback | `improvement_before_after_images/04_common_mistake_feedback_after.png` |
| Teacher suggested visual representations | Added function graph interpretation for linear and quadratic functions | `application_screenshots/01_homepage.png` |
| Students wanted more useful practice | Added adaptive recommendations and progress tracking | `application_screenshots/05_progress_dashboard.png` |

## Example Improvement Explained

Student feedback said practice questions were too easy and followed similar
patterns. In response, the system was expanded beyond simple linear equations.

Example supported task:

```text
Find the gradient between (2, 3) and (6, 11).
```

Correct method:

```text
gradient = change in y / change in x
gradient = (11 - 3) / (6 - 2)
gradient = 8 / 4
gradient = 2
```

If a student answers `1/2`, the system detects a likely misconception: the
student used run over rise instead of rise over run. It gives targeted
feedback, records the mistake pattern, updates the coordinate geometry skill,
and recommends further practice.

This is stronger than simple right/wrong checking because it identifies a
specific learning issue.

## Verification

Latest automated test result:

```text
python -m unittest discover -s tests
Ran 90 tests in 7.561s
OK
```

Test result screenshot:

```text
application_screenshots/07_test_results.png
```

## Remaining Limitations

- The platform is strongest for supported algebra, graph, and coordinate
  geometry workflows.
- It is not a replacement for a teacher or for a general AI system like
  ChatGPT.
- Some unusual wording or advanced questions may still be unsupported.
- The misconception engine is rule-based, so it detects clear patterns but does
  not fully understand every possible student method.
- More tester feedback would be needed before making claims about learning
  outcomes.

## Honest Application Summary

The platform was tested by a mathematics teacher and several students. Their
feedback showed that the project was clear and useful, but also identified
weaknesses in difficulty, layout, working space, visual support, and mistake
feedback. I used this feedback to guide later improvements, including harder
practice generation, step-working validation, graph interpretation, coordinate
geometry practice, progress tracking, and misconception feedback.
