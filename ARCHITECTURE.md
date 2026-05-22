# Architecture

This project is a Flask homework helper with a modular tutoring backend. The
main goal of the architecture is to keep web routing, classification, subject
engines, math solving, formatting, and student progression separate enough that
each part can be tested and improved safely.

## Request Flow

1. A browser sends a request to `app.py`.
2. Flask route handlers validate the request payload.
3. `homework_helper.py` preserves backwards-compatible imports and delegates to
   the modular backend.
4. `core/router.py` orchestrates the request:
   - records question activity,
   - checks experiment scope,
   - resolves answer mode,
   - dispatches to the relevant subject engine.
5. Subject engines in `engine/` produce the response.
6. Flask returns JSON or renders a template.

## Top-Level Files

- `app.py`: Flask application, HTTP routes, feedback logging, and JSON
  responses.
- `homework_helper.py`: compatibility wrapper for older imports. It should stay
  thin and should not contain business logic.
- `Procfile`: production start command for platforms such as Render.
- `requirements.txt`: direct Python dependencies needed to run and test the
  project.
- `.python-version`: Python version used for consistent local and hosted
  deployment behavior.

## Core Package

- `core/router.py`: orchestration layer. It decides how a question should be
  handled and delegates to engines.
- `core/classifier.py`: deterministic subject, intent, topic, mode, and keyword
  classification. No ML model is required.
- `core/parser.py`: shared SymPy parsing and equation normalization helpers.
- `core/validator.py`: expression equivalence, equation equivalence, and
  algebra step validation.
- `core/progression.py`: in-memory student profile, stats, skill progression,
  and adaptive problem generation.
- `core/understanding.py`: legacy understanding utility. Classification calls
  delegate back to `core/classifier.py`.

## Engine Package

- `engine/math_engine.py`: public facade for math behavior. Existing imports
  should continue to use this file.
- `engine/algebra_solver.py`: algebra solver primitives such as linear,
  quadratic, simultaneous equations, factoring, and symbolic solving.
- `engine/math_answer_checker.py`: answer evaluation and diagnostic feedback.
- `engine/math_practice.py`: guided practice session helpers.
- `engine/math_modes.py`: direct, step-by-step, and hint responses for algebra
  prompts.
- `engine/math_workflows.py`: legacy chat-style math commands such as step
  recording, hints, factoring prompts, and practice requests.
- `engine/science_engine.py`: science explanations and formula handling.
- `engine/english_engine.py`: English writing and TEEL scaffolding.
- `engine/humanities_engine.py`: humanities and study-note responses.
- `engine/lesson_engine.py`: lesson catalog lookup and lesson rendering.
- `engine/fallback_engine.py`: generic study-help fallback responses.

## Data And Utilities

- `data/constants.py`: subject keywords, follow-up prompts, experiment messages,
  and lesson catalog content.
- `data/intents.py`: intent metadata only: patterns, keywords, topic, engine,
  difficulty, and examples.
- `utils/formatting.py`: shared user-facing formatting helpers.

## Testing Strategy

The current tests focus on public behavior rather than implementation details:

- Flask endpoints still return the expected JSON shape.
- Algebra direct, hint, and step-by-step modes still work.
- Answer checking still accepts assignment-style answers such as `x = 3`.
- Step validation still catches invalid transformations.
- Lesson catalog responses still include rich lesson payloads.

Run:

```powershell
python -m unittest
```

## Deployment Notes

The app is ready for a basic Render deployment:

- Flask app object: `app:app`
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Python version: `3.11.9`

Feedback logs are currently stored in `feedback_log.json`. Render's normal
filesystem should be treated as temporary between deploys and service restarts,
so production feedback should eventually move to a database or external store.

## Remaining Architecture Risks

- Student progression is stored in process memory, so it is not ready for
  multiple real users.
- Feedback persistence uses a local JSON file. That is acceptable for a demo,
  but weak for production.
- `math_modes.py` is still the largest math module and may eventually deserve
  smaller per-topic handlers.
- Compatibility wrappers are useful now, but new code should import from
  `core/` and `engine/` directly.

## Next Best Step

Add persistent storage for feedback and student progress. For a school demo,
the simplest production-minded improvement is a small database-backed model for
feedback submissions and practice attempts.
