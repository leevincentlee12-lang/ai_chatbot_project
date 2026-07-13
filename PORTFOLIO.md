# Adaptive Algebra Learning Platform Project Write-Up

This file is a project write-up for applications and presentations. It is not a
CV. A CV describes the student. This document describes one project: what was
built, why it was built, how it works, what feedback was received, and what can
be improved next.

Public demo: https://ai-chatbot-project-tlou.onrender.com

## One-Sentence Summary

I built a deployed adaptive algebra learning platform that gives structured
explanations, hints, generated practice, answer checking, and progress tracking
for students learning algebra.

## Why I Built It

Students often need help while doing homework or revision, but receiving only a
final answer does not always support learning. This project focuses on showing
the method, explaining why each step works, and giving students a way to
practise and check their understanding.

## Main Features

- Step-by-step algebra explanations
- Hint Mode for students who want to think independently first
- Direct mode for quick answer checking
- Practice Mode with generated algebra problems
- Answer checking with feedback for incorrect answers
- Working-space validation for student method lines
- Lesson pages with worked examples and common mistakes
- Progress page showing accuracy, difficulty, skills, and recent activity
- Function graph interpretation for supported linear and quadratic functions
- Coordinate geometry practice for midpoint, gradient, distance, and line equations
- Rule-based misconception feedback for selected algebra, graph, and coordinate errors

## Teacher Feedback

Teacher feedback highlighted that the platform's mathematical reasoning was
accurate, the algebraic methods were appropriate, and the step-by-step
explanations were clear and easy to follow.

The feedback also suggested three future improvements:

- More feedback for common mistakes
- More visual representations, such as graphs
- A wider variety of question difficulties

I used this feedback to identify the next development priorities.

## What I Improved After Feedback

- Tested realistic student and teacher prompts
- Fixed a leading-negative parsing bug in worded equations
- Improved topic labels for quadratics, factoring, and trigonometry
- Improved follow-up prompts so they are more specific and useful
- Added graph interpretation after teacher feedback requested more visual representations
- Added coordinate geometry and graph-feature practice problems
- Added targeted feedback for reversed gradient, missing square root, midpoint, and graph-feature mistakes
- Added regression tests for the bugs found during testing
- Captured updated screenshots from the running application

## Evidence of Testing

The project includes automated tests for the main learning workflows.

Latest verification:

```text
90 tests passed
```

Tested manually with examples including:

- `find x in -6x + 2 = 8x - 82`
- `solve 3x^2 - 4x - 4 = 0`
- `factor x^2 - 9`
- `find x if sin 35 = x/12`
- `question: x^2 - 5x + 6 = 0 answer: x = 2`
- `explain the graph of y = x^2 - 4x + 3`
- `find the equation of the line through (2, 3) and (6, 11)`
- `Find the gradient between (2, 3) and (6, 11)` with an incorrect answer of `1/2`

## Demo Flow

1. Open the homepage and explain the purpose of the platform.
2. Ask a hard algebra question, such as `solve 3x^2 - 4x - 4 = 0`.
3. Show the structured response and follow-up prompts.
4. Submit a wrong answer and show the diagnostic feedback.
5. Open Practice Mode and generate a hard problem.
6. Open the Progress page to show recorded learning activity.
7. Open the About page to explain the architecture.

## Screenshot Set

| Purpose | File |
| --- | --- |
| Homepage | `static/screenshots/homepage.png` |
| Solving equations | `static/screenshots/solving-equations.png` |
| Hard equation demo | `static/screenshots/demo-hard-equation.png` |
| Wrong answer feedback | `static/screenshots/demo-wrong-answer-feedback.png` |
| Practice mode | `static/screenshots/practice-mode.png` |
| Practice progress | `static/screenshots/demo-practice-progress.png` |
| Lessons | `static/screenshots/lessons-page.png` |
| Progress dashboard | `static/screenshots/dashboard.png` |
| Architecture | `static/screenshots/architecture.png` |
| Automated test results | `application_screenshots/07_test_results.png` |

## Architecture Summary

```text
User Input
  -> Router
  -> Subject Engine
  -> Solver
  -> Feedback Generator
  -> Progress Tracking
```

The project uses Flask for the backend, SymPy for algebra support, SQLite for
learning state, and HTML/CSS/JavaScript for the frontend.

## Honest Limitations

This platform is not a full replacement for a teacher or a general AI system.
It is strongest as a focused algebra learning tool. Some advanced or unusual
questions may still be unsupported.

## Future Improvements

- Add more visual representations inside individual response cards
- Improve common mistake detection after further student testing
- Add more Year 10 and Year 11 level problem generators
- Add teacher-facing summaries if the learning data model becomes stronger
- Improve long-term data storage if user accounts are added later
