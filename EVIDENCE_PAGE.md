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
- fixing a leading-negative parsing bug in worded equations
- improving topic labels for quadratics, factoring, and trigonometry
- adding regression tests for important bugs and algebra workflows
- capturing updated screenshots from the running application

Current verification:

```text
64 automated tests passed
```

Next planned improvements:

- add graph visuals for linear and quadratic equations
- improve common mistake feedback
- add more Year 10 and Year 11 style questions
- improve teacher-facing summaries if the learning data model becomes stronger
