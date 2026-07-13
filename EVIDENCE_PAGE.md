# Evidence Page: Adaptive Algebra Learning Platform

## Project Summary

I built an Adaptive Algebra Learning Platform to support students with algebra
revision, homework, and independent practice. The platform provides
step-by-step explanations, Hint Mode, generated practice questions, answer
checking, lesson pages, and progress tracking.

The project was developed from a simple homework helper into a focused
educational platform. I refactored the code into separate modules for routing,
classification, algebra solving, validation, lessons, progression, and frontend
presentation. The platform is publicly deployed using Render and GitHub.

The main goal is to help students understand the reasoning behind algebraic
methods, rather than only giving a final answer. Responses are organised into
clear learning sections such as Answer, Method, Why, Check, and Next Step.

## Screenshot

Suggested screenshot to include:

`static/screenshots/solving-equations.png`

This screenshot shows the platform solving a quadratic equation with structured
feedback and follow-up prompts.

Other useful screenshots:

- `static/screenshots/homepage.png`
- `static/screenshots/practice-mode.png`
- `static/screenshots/demo-wrong-answer-feedback.png`
- `static/screenshots/dashboard.png`
- `static/screenshots/architecture.png`

## Teacher Feedback

I received feedback from a mathematics teacher who reviewed the project as a
student learning tool.

The teacher noted that:

- the mathematical reasoning appeared accurate
- the examples followed appropriate algebraic methods
- the explanations were clear and easy to follow
- Step-by-step Mode was especially clear
- Hint Mode was the most useful feedback mode because it encourages students to
  think independently before receiving more support
- the platform could be useful for revision, homework, and independent practice

The teacher also suggested future improvements:

- add feedback for common mistakes
- add visual representations such as graphs
- include a wider variety of question difficulties

## Improvements Made

Based on testing and feedback, I improved the project by:

- making the homepage clearer and more academic
- improving response formatting into Answer, Method, Why, Check, and Next Step
- adding Practice Mode with generated problems and retry support
- adding answer checking with feedback for incorrect answers
- adding a working-space feature for step-by-step student working
- adding a Progress page for accuracy, difficulty, skill scores, and recent activity
- improving algebra intent routing
- improving hard practice questions with quadratics and rational equations
- adding graph interpretation for gradients, intercepts, vertices, axes of symmetry, and discriminants
- adding coordinate geometry support for midpoint, gradient, distance, and equations of lines
- extending Practice Mode so graph and coordinate geometry questions can be generated and checked
- adding misconception feedback for reversed gradient, incomplete midpoint averaging, missing square roots in distance, and graph-feature confusion
- fixing a leading-negative parsing bug in worded equations
- improving topic labels for quadratics, factoring, and trigonometry
- adding regression tests for important bugs and algebra workflows
- capturing updated screenshots from the running application

Current verification:

```text
90 automated tests passed
```

Next planned improvements:

- add more visual representations inside individual response cards
- improve common mistake feedback using more student testing evidence
- add more Year 10 and Year 11 style questions
- improve teacher-facing summaries if the learning data model becomes stronger

## Example Explanation For Applications

Before this improvement, Practice Mode mostly generated algebra-equation
questions. That meant graph and coordinate geometry features could be explained
in chat, but were not yet integrated into the adaptive practice workflow.

After the improvement, Practice Mode can generate and check questions such as:

```text
Find the gradient between (2, 3) and (6, 11).
```

If a student answers `1/2`, the system recognises that the student likely used
run over rise instead of rise over run. The feedback explains the issue,
records the misconception, updates the coordinate geometry skill score, and
recommends targeted practice.

This matters because it shows the project moving from a simple solver toward a
learning system that can detect specific patterns in student mistakes.

## Screenshot Evidence Set

Use these screenshots in the application evidence section:

- Homepage: `static/screenshots/homepage.png`
- Step-by-step solution: `application_screenshots/02_step_by_step_solution.png`
- Wrong answer feedback: `application_screenshots/03_wrong_answer_feedback.png`
- Practice Mode: `application_screenshots/04_practice_mode.png`
- Progress dashboard: `application_screenshots/05_progress_dashboard.png`
- Architecture: `application_screenshots/06_architecture.png`
- Automated test results: `application_screenshots/07_test_results.png`

Useful before/after improvement images:

- `improvement_before_after_images/02_harder_practice_before_after.png`
- `improvement_before_after_images/03_working_space_before_after.png`
- `improvement_before_after_images/04_common_mistake_feedback_after.png`
- `improvement_before_after_images/05_progress_tracking_after.png`

## Technical Learning

Through this project I learned how to:

- separate a large Flask project into smaller modules with clearer responsibilities
- use deterministic routing and intent classification instead of large chains of fragile if-statements
- use SymPy to parse and compare algebraic expressions and equations
- avoid rounding errors by preserving exact fractions in coordinate geometry
- build regression tests for bugs found through real testing
- connect answer checking to progress tracking, misconception history, and adaptive recommendations
- deploy a Flask project publicly using GitHub and Render
