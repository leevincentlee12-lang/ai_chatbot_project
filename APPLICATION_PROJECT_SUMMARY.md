# Adaptive Algebra Learning Platform

## Project Summary

I built an Adaptive Algebra Learning Platform to support students with algebra
revision, homework, and independent practice. The platform provides structured
explanations, hint-based support, generated practice questions, answer checking,
lesson pages, and progress tracking.

The project started as a simple homework helper and was developed into a more
focused educational platform. I refactored the code into separate modules for
routing, classification, algebra solving, validation, lessons, progression, and
frontend presentation. The platform is publicly deployed on Render and uses
Flask, SymPy, SQLite, HTML, CSS, and JavaScript.

The main educational goal is to help students understand algebraic reasoning,
not just receive final answers. Responses are organised into clear learning
sections such as answer, method, why, check, and next step.

## Screenshot

Recommended screenshot to include in the application:

![Solving equations screenshot](static/screenshots/solving-equations.png)

Other useful screenshots:

- Homepage: `static/screenshots/homepage.png`
- Practice Mode: `static/screenshots/practice-mode.png`
- Wrong answer feedback: `static/screenshots/demo-wrong-answer-feedback.png`
- Progress dashboard: `static/screenshots/dashboard.png`
- System architecture: `static/screenshots/architecture.png`
- Automated test results: `application_screenshots/07_test_results.png`

## Teacher Feedback

I received feedback from a mathematics teacher who reviewed the project as a
student learning tool. The teacher noted that the examples tested appeared
mathematically accurate and followed appropriate algebraic methods. They also
said the explanations were clear and easy to follow, especially in
step-by-step mode.

The teacher identified Hint Mode as the most useful feedback mode because it
encourages students to think independently before receiving more support. They
also said the platform could be useful for revision, homework, and independent
practice because it provides immediate feedback and supports students at
different levels.

The suggested improvements were to add more feedback for common mistakes, add
more visual representations such as graphs, and include a wider variety of
question difficulties.

## Improvements Made

After testing the platform and receiving feedback, I made several improvements:

- Added a clearer academic homepage and project identity
- Added structured response formatting for answer, method, why, check, and next step
- Added Practice Mode with generated problems, retry support, and answer checking
- Added a working-space feature so students can enter step-by-step working
- Added a Progress page showing accuracy, difficulty, skill scores, and recent activity
- Improved the intent routing system for algebra requests
- Improved support for harder algebra problems, including quadratics and rational equations
- Added graph interpretation for linear and quadratic functions
- Added coordinate geometry support for midpoint, gradient, distance, and line equations
- Extended Practice Mode with graph and coordinate geometry practice checking
- Added targeted feedback for graph and coordinate geometry mistake patterns
- Fixed bugs found during testing, including a leading-negative parsing issue
- Improved topic labelling for quadratics, factoring, and trigonometry
- Added regression tests to check important algebra and routing behaviour
- Captured updated screenshots from the running application

Current verification:

```text
90 automated tests passed
```

Next improvements planned:

- Add more visual representations inside individual answer cards
- Improve feedback for more student mistake patterns after further testing
- Add more Year 10 and Year 11 style problem generators
- Improve teacher-facing summaries if the learning data model becomes stronger

## Technical Learning

This project helped me learn how to structure a Flask application into modules,
use deterministic intent routing, work with symbolic mathematics through SymPy,
store learning state in SQLite, build automated regression tests, and connect
student answers to progress tracking and misconception feedback.
