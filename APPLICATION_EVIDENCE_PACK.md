# Application Evidence Pack

## Project Summary

I built a deployed adaptive algebra learning platform that supports structured
explanations, Hint Mode, generated practice, answer checking, lesson pages,
progress tracking, graph interpretation, coordinate geometry practice, and
rule-based misconception feedback.

The project began as a simple homework-helper app and was developed into a more
modular educational platform. The main goal is to help students understand
mathematical reasoning rather than only receiving final answers.

## Clear Example To Explain

Example prompt:

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

If a student answers `1/2`, the system identifies a likely reversed-gradient
mistake. It explains that the student may have used run over rise instead of
rise over run, records the misconception, updates the coordinate geometry
skill score, and recommends targeted practice.

This shows the project moving beyond a basic solver toward an adaptive learning
system that can detect specific mistake patterns.

## Screenshot Evidence

Use these screenshots:

| Evidence | File |
| --- | --- |
| Homepage | `application_screenshots/01_homepage.png` |
| Step-by-step solving | `application_screenshots/02_step_by_step_solution.png` |
| Wrong answer feedback | `application_screenshots/03_wrong_answer_feedback.png` |
| Practice Mode | `application_screenshots/04_practice_mode.png` |
| Progress dashboard | `application_screenshots/05_progress_dashboard.png` |
| Architecture | `application_screenshots/06_architecture.png` |
| Automated tests | `application_screenshots/07_test_results.png` |

Before/after improvement screenshots:

| Improvement | File |
| --- | --- |
| General question handling | `improvement_before_after_images/01_general_question_handling_before_after.png` |
| Harder practice questions | `improvement_before_after_images/02_harder_practice_before_after.png` |
| Working space for steps | `improvement_before_after_images/03_working_space_before_after.png` |
| Common mistake feedback | `improvement_before_after_images/04_common_mistake_feedback_after.png` |
| Progress tracking | `improvement_before_after_images/05_progress_tracking_after.png` |

## Test Result Evidence

Latest verification:

```text
python -m unittest discover -s tests
Ran 90 tests in 7.561s
OK
```

The tests cover routing, algebra solving, answer checking, Practice Mode,
graph and coordinate practice, misconception tracking, lessons, progress pages,
and API endpoints.

## Improvements Made From Feedback

- Added clearer educational response sections: Answer, Method, Why, Check, and Next Step
- Added Practice Mode with generated questions and answer checking
- Added working space for student steps before final answers
- Added progress tracking for accuracy, difficulty, skill scores, and recent activity
- Added misconception feedback for common algebra mistakes
- Added graph interpretation for linear and quadratic functions
- Added coordinate geometry support and practice checking
- Added automated regression tests for important workflows and bugs

Detailed feedback analysis:

```text
FEEDBACK_EVALUATION.md
```

## Technical Learning

I learned how to:

- refactor a Flask project into smaller modules with clearer responsibilities
- design deterministic intent routing without using machine learning
- use SymPy for parsing, solving, and checking mathematical equivalence
- preserve exact fractions in coordinate geometry instead of relying on rounded decimals
- connect answer checking to skill progression and misconception history
- write automated tests to prevent old bugs from returning
- deploy a Flask application publicly using GitHub and Render

## Honest Limitations

The project is strongest for supported algebra, graph, and coordinate geometry
tasks. It is not a full general-purpose mathematics tutor yet. Some advanced
or unusual questions may still be unsupported, so future development should be
guided by more student testing rather than adding random features.
