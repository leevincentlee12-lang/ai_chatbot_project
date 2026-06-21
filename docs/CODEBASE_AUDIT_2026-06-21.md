# Codebase Audit

Date: 2026-06-21

## Executive Assessment

The project is a credible deployed prototype with a clear educational purpose.
It has working modular packages, user-scoped SQLite state, structured algebra
responses, practice workflows, and 64 passing automated tests.

The main weakness is no longer basic functionality. It is the gap between the
current product claims and the evidence behind them. In particular:

- adaptive practice is not yet skill-targeted,
- mastery scores are simple counters rather than validated estimates,
- untrusted mathematical input reaches SymPy without a strong safety boundary,
- student data and feedback do not yet have appropriate governance,
- overlapping routing and solving paths make future changes risky.

The project should not be rewritten. The safest strategy is to strengthen one
boundary at a time while preserving the public API and existing tests.

## Verification Performed

- `python -m unittest discover -s tests`
  - Result: 64 tests passed.
- Python compile check across application, core, engine, data, utilities, and
  tools.
  - Result: passed.
- Repository structure, dependencies, persistence, routing, parser, validation,
  progression, feedback, frontend, and deployment configuration reviewed.

## Ranking Scale

- Impact: effect on learning value, reliability, privacy, or scalability.
- Difficulty: expected implementation effort.
- Change risk: likelihood of breaking existing behaviour without careful tests.

## Top 10 Improvements

### 1. Make Adaptation Genuinely Skill-Targeted

Impact: Critical

Difficulty: High

Change risk: Medium

Evidence:

- `core/progression.py:551-562` finds the weakest skill, stores it as the
  current topic, and then calls the same difficulty-based random generator.
- `core/progression.py:530-544` chooses problems only from difficulty bands.
- `engine/math_answer_checker.py:200-208` and `236-242` adjust mastery using
  fixed `+5` and `-3` changes.

Why it matters:

The current system can display skill scores and difficulty changes, but it does
not reliably generate a problem for the skill it identified as weak. This is
the central gap between an algebra chatbot and an adaptive learning system.

Files affected:

- `core/progression.py`
- `core/state_store.py`
- `engine/math_answer_checker.py`
- `static/practice.js`
- `tests/test_ai.py`
- `tests/test_state_store.py`

New components:

- `ProblemSpec` data class containing skill, difficulty, problem, solution, and
  generator metadata.
- `select_target_skill(user_id)` function.
- `select_problem_generator(skill, difficulty)` function.
- `record_skill_evidence(...)` function.

Implementation steps:

1. Create an explicit registry mapping each skill to supported generators.
2. Separate skill selection from difficulty selection.
3. Generate problems from the selected skill registry.
4. Store outcome evidence including skill, difficulty, correctness, hint use,
   attempts, and timestamp.
5. Replace raw mastery changes with a documented rule that considers attempts
   and recent evidence.
6. Keep the current score field for compatibility while deriving it from the
   evidence model.

Verification:

- Set quadratics as the weakest skill and assert the next adaptive problem is a
  quadratic.
- Simulate repeated correct and incorrect answers and verify predictable score
  movement.
- Verify new users do not receive a misleading strongest or weakest skill
  before enough evidence exists.

Potential risks:

- Existing dashboard values may change.
- Sparse evidence can produce unstable recommendations.
- Unsupported skills need an explicit fallback instead of silent randomisation.

### 2. Create a Safe, Bounded Mathematical Input Boundary

Impact: Critical

Difficulty: Medium

Change risk: High

Evidence:

- `core/parser.py:46-59` passes user input directly to SymPy `parse_expr`.
- `app.py:206-233` and `374-391` do not set request, expression, or step-count
  limits.
- Public routes can trigger symbolic simplification and solving with no
  execution budget.

Why it matters:

`parse_expr` uses Python evaluation internally and is not designed as a secure
parser for arbitrary public input. Large or adversarial symbolic expressions
can also consume excessive CPU or memory and make the service unavailable.

Files affected:

- `core/parser.py`
- `core/validator.py`
- `engine/algebra_solver.py`
- `app.py`
- `tests/test_ai.py`

New components:

- `MathInputPolicy` with maximum length, allowed symbols, allowed functions,
  maximum exponent, and maximum nesting.
- `validate_math_syntax(text)` function.
- `MathInputRejected` exception.

Implementation steps:

1. Add application-level JSON and question length limits.
2. Tokenise and validate input before symbolic parsing.
3. Allow only the syntax required by supported school mathematics.
4. Provide a restricted SymPy local and global namespace.
5. Reject excessive exponents, nesting, variable counts, and step counts.
6. Add rate limiting before public deployment is used by larger groups.
7. Consider moving expensive symbolic work to a worker process with a timeout.

Verification:

- Test accepted school notation such as `2x`, `x^2`, fractions, and brackets.
- Test rejected names, attributes, imports, oversized exponents, deeply nested
  input, long strings, and excessive validation steps.
- Load-test repeated `/ask` and `/check-answer` requests.

Potential risks:

- A strict policy can reject valid notation students currently use.
- Parser changes affect almost every math workflow, so they need a compatibility
  corpus before release.

### 3. Add Privacy, Consent, and Session Security for Student Data

Impact: Critical

Difficulty: Medium

Change risk: Medium

Evidence:

- `app.py:32-35` uses a known fallback session secret.
- `app.py:56-60` stores the user identity in the client-side Flask session.
- `core/state_store.py:116-158` stores questions, mistakes, submitted answers,
  and step history.
- `static/script.js:324-332` sends the original question with feedback.
- `feedback_log.json` is currently tracked by Git.
- No consent, retention, export, or deletion workflow was found.

Why it matters:

The target users are students, including minors. Even anonymous learning
history can become sensitive when it contains free-text questions, mistakes,
and timestamps. A forged session is also possible if a deployment uses the
known fallback secret.

Files affected:

- `app.py`
- `core/state_store.py`
- `templates/about.html`
- `templates/index.html`
- `.gitignore`
- deployment configuration

New components:

- `require_production_secret(app)` startup validation.
- Data retention and deletion service.
- Privacy notice and optional research-consent record.

Implementation steps:

1. Refuse production startup when `SECRET_KEY` is missing.
2. Configure secure, HTTP-only, same-site cookies.
3. Remove `feedback_log.json` from version control and keep it ignored.
4. Define which fields are necessary and stop storing unnecessary raw text.
5. Add retention periods for recent questions, mistakes, and feedback.
6. Add a "clear my learning data" action.
7. Separate normal product use from optional research data collection.
8. Document who can access collected data.

Verification:

- Test that production configuration fails without a secret.
- Test that a modified session cookie is rejected.
- Test deletion removes all rows for a user.
- Confirm no user-generated data appears in `git ls-files`.

Potential risks:

- Removing raw text can reduce diagnostic and research usefulness.
- Deletion must cover every table and external feedback destination.

### 4. Replace Demo Persistence With a Reliable Data Layer

Impact: High

Difficulty: High

Change risk: Medium

Evidence:

- `app.py:70-94` reads and rewrites the entire feedback JSON file.
- `app.py:257-264` performs an unlocked read-modify-write sequence.
- `core/state_store.py:73-161` creates the schema directly in application code
  with no schema version or migration process.
- `core/state_store.py:285-292` reads then rewrites skill state in separate
  transactions, allowing lost updates under concurrency.
- `ARCHITECTURE.md:105-120` already identifies local storage as temporary.

Why it matters:

Concurrent workers can overwrite feedback or skill updates. Local files also do
not support reliable multi-instance deployment, durable analytics, or research
datasets.

Files affected:

- `app.py`
- `core/state_store.py`
- `requirements.txt`
- deployment documentation
- tests

New components:

- Repository interfaces for learning state, attempts, and feedback.
- Schema migration tooling.
- Transactional `record_attempt(...)` operation.

Implementation steps:

1. Move feedback records into the database.
2. Add an `attempt_events` table rather than updating several counters
   independently.
3. Make attempt, skill, progression, and mistake updates one transaction.
4. Add schema versions and migrations.
5. Keep SQLite for local development and tests.
6. Add a managed PostgreSQL implementation for production when durable
   multi-user data is required.
7. Add a health endpoint that checks application and database readiness.

Verification:

- Run concurrent answer submissions and verify no updates are lost.
- Restart the deployed service and verify durable state remains.
- Run migrations from an older database copy.
- Test rollback when one part of an attempt update fails.

Potential risks:

- Data migration can lose existing demonstration data if not backed up.
- Supporting SQLite and PostgreSQL can create dialect differences.

### 5. Consolidate Duplicate Routing, Classification, and Solving Paths

Impact: High

Difficulty: High

Change risk: High

Evidence:

- `data/intents.py` and `engine/math_workflows.py:570-746` define separate intent
  systems.
- `core/router.py:319-422` chooses between workflow handling and mode handling.
- `engine/math_modes.py` and `engine/algebra_solver.py` both implement topic
  solving and explanation logic.
- Equation-wrapper stripping exists in multiple modules.
- `core/router.py:164-280` contains another large topic-specific decision tree
  for follow-up generation.

Why it matters:

The same request can travel through different handlers depending on wording.
Every new topic or prompt must be added in several places, creating regressions
such as incorrect labels, dropped negative signs, or dead follow-up buttons.

Files affected:

- `core/classifier.py`
- `core/router.py`
- `data/intents.py`
- `engine/math_workflows.py`
- `engine/math_modes.py`
- `engine/algebra_solver.py`

New components:

- One `IntentDefinition` registry with matcher, topic, capability, and handler.
- Structured `TutorResponse` model.
- One normalised `MathRequest` model.

Implementation steps:

1. Define a structured request and response contract.
2. Move all intent metadata into one ordered registry.
3. Make each intent point to one handler.
4. Keep solver primitives separate from educational presentation.
5. Generate follow-ups from response metadata instead of parsing response text.
6. Remove duplicated prompt-stripping helpers after parity tests pass.
7. Preserve compatibility exports until callers are migrated.

Verification:

- Build a prompt corpus and assert one intended route per prompt.
- Compare current and new responses for existing supported requests.
- Add tests that every follow-up prompt routes to a non-error handler.

Potential risks:

- Intent order changes behaviour.
- A large one-step migration would be unsafe; move one intent family at a time.

### 6. Isolate Tests and Expand Correctness Coverage

Impact: High

Difficulty: Medium

Change risk: Low

Evidence:

- `tests/test_ai.py:19-23` creates a Flask client without configuring a temporary
  database.
- Many tests call state-changing functions without a unique user ID.
- `tests/test_state_store.py:12-50` uses unique IDs but still writes to the
  default application database.
- No tests were found for parser security, concurrency, migrations, privacy,
  adaptive skill targeting, or rate limits.

Why it matters:

Tests currently mutate the same local database used by manual demonstrations.
Passing tests prove many workflows work, but not that the system is safe under
adversarial input, concurrent use, deployment changes, or statistically valid
adaptation.

Files affected:

- `tests/`
- `app.py`
- `core/state_store.py`
- test configuration

New components:

- Application factory fixture.
- Temporary database fixture.
- Prompt corpus and generated algebra properties.

Implementation steps:

1. Create `create_app(config)` and inject a temporary database path in tests.
2. Reset database initialisation state between test databases.
3. Split tests into unit, integration, security, and end-to-end groups.
4. Add property-based tests for generated problems and answer validation.
5. Add regression cases for every production bug found.
6. Add CI that runs tests and compile checks on each push.

Verification:

- Confirm test runs do not change `instance/homework_helper.sqlite3`.
- Run tests repeatedly in random order.
- Run parallel test jobs.
- Confirm generated problems always have valid declared solutions.

Potential risks:

- Existing tests may rely on shared state accidentally.
- Test refactoring can expose hidden coupling before product code changes.

### 7. Build a Structured Misconception and Hint-Ladder System

Impact: High

Difficulty: High

Change risk: Medium

Evidence:

- `engine/math_answer_checker.py:62-152` uses a small set of numeric heuristics
  for misconception diagnosis.
- `core/validator.py:108-119` chooses hints mainly by checking whether a string
  contains `+`, `-`, or `x`.
- `engine/math_practice.py:22-27` gives one generic retry message.
- Teacher feedback specifically prioritised Hint Mode and common-mistake
  feedback.

Why it matters:

This is the highest-value educational improvement after genuine adaptation.
Useful hints should respond to a diagnosed misconception and reveal support
gradually, rather than repeat a generic rule or show the answer immediately.

Files affected:

- `engine/math_answer_checker.py`
- `core/validator.py`
- `engine/math_practice.py`
- `core/state_store.py`
- frontend response components

New components:

- `MisconceptionCode` definitions.
- `Diagnosis` model with evidence and confidence.
- `HintPolicy` with progressive levels.

Implementation steps:

1. Define a small misconception taxonomy for linear equations first.
2. Diagnose from submitted working where possible, not only the final number.
3. Store misconception codes instead of only free-text issue descriptions.
4. Provide hint levels: strategic prompt, operation reminder, partial setup,
   then worked step.
5. Record which hint level was requested and whether the next attempt improved.
6. Expand to quadratics only after linear diagnostics are evaluated.

Verification:

- Create labelled examples for each misconception.
- Ask teachers to rate diagnosis and hint usefulness.
- Measure correction rate after each hint level.
- Track false diagnoses and allow "this feedback did not match my mistake".

Potential risks:

- Incorrect diagnosis can teach the wrong lesson.
- Too many categories will be difficult to validate with a small tester group.

### 8. Introduce an Application Factory and Explicit Service Boundaries

Impact: Medium-High

Difficulty: Medium

Change risk: Medium

Evidence:

- `app.py` combines configuration, routes, feedback persistence, external HTTP
  calls, session identity, analytics, and error handling.
- `app.py:18-29` imports through the broad compatibility facade.
- `homework_helper.py:21-178` dynamically re-exports a large internal surface.
- Legacy files such as `intent_classifier.py`, `training_data.py`,
  `test_ai_backup.py`, `debug_intent.py`, and `templates/learn.html` remain.
- Generated Chrome profile data occupies about 71 MB under `instance/`.

Why it matters:

Implicit dependencies make tests harder to isolate and new services harder to
replace. Repository clutter also makes the project appear less deliberate to
technical reviewers.

Files affected:

- `app.py`
- `homework_helper.py`
- top-level compatibility files
- future `routes/`, `services/`, and `models/` packages

New components:

- `create_app(config=None)` application factory.
- Flask blueprints for learning, practice, lessons, progress, and feedback.
- Services for tutoring, progression, feedback, and analytics.

Implementation steps:

1. Add an application factory without moving routes initially.
2. Inject configuration and repositories.
3. Move one route group at a time into blueprints.
4. Change `app.py` to a thin production entry point.
5. Make new code import explicit modules instead of `homework_helper.py`.
6. Mark compatibility modules deprecated, then remove them after usage checks.
7. Remove generated browser-profile data from the workspace.

Verification:

- Existing endpoint tests must pass after each route group moves.
- Import smoke tests must cover old compatibility imports.
- Run the Render start command locally after each phase.

Potential risks:

- Moving routes can change endpoint names used by templates.
- Removing compatibility files too early can break external or hidden callers.

### 9. Make Analytics Valid Enough for Educational Evaluation

Impact: Medium-High

Difficulty: Medium

Change risk: Low

Evidence:

- `app.py:321-333` records a lesson as completed whenever its API or page is
  opened.
- `app.py:287-307` analytics only reports feedback count, average rating, and
  subject distribution.
- Current progress is based on counters rather than a documented event model.
- There is no pre-test, post-test, delayed retention check, or comparison
  condition.

Why it matters:

The project cannot claim learning effectiveness from usage counts or ratings.
Valid research requires clear event definitions and outcome measures.

Files affected:

- `app.py`
- `core/state_store.py`
- `core/progression.py`
- analytics frontend
- documentation

New components:

- `learning_events` table.
- Event definitions such as problem_started, hint_requested, step_submitted,
  answer_checked, lesson_started, and lesson_completed.
- Research export with anonymised aggregate data.

Implementation steps:

1. Define events before building more dashboards.
2. Stop treating page opens as lesson completions.
3. Record timestamps, skill, difficulty, mode, attempts, hints, and outcome.
4. Add completion rules for lessons and practice sequences.
5. Build aggregate reports from events.
6. Design small pre/post studies before claiming educational impact.

Verification:

- Test each user action records exactly one expected event.
- Reconstruct summary counters from events and compare with displayed values.
- Manually audit a small session against the event log.

Potential risks:

- Over-collection increases privacy risk.
- Metrics can influence product behaviour even when they are not educationally
  meaningful.

### 10. Add Pedagogically Useful Visuals and Improve Hint-First UX

Impact: Medium

Difficulty: Medium

Change risk: Low

Evidence:

- `templates/index.html:67-70` defaults to Step-by-Step Mode.
- Teacher feedback identified Hint Mode as the most useful mode.
- Teacher feedback also requested graph-based visual representations.
- Current output is primarily text, buttons, and progress cards.

Why it matters:

Graphs can connect symbolic equations to mathematical meaning. A hint-first
default can also reduce answer dependence, but both changes should be evaluated
rather than assumed to improve learning.

Files affected:

- `templates/index.html`
- `static/script.js`
- `static/style.css`
- new graph component or service
- research documentation

New components:

- Graph specification returned by supported math handlers.
- Accessible graph renderer for linear and quadratic functions.
- Hint-first experiment configuration.

Implementation steps:

1. Start with linear and quadratic graphs only.
2. Return structured graph data, not HTML generated by the solver.
3. Display axes, intercepts, roots, turning points, and accessible text
   summaries.
4. Add "show graph" only when it supports the current learning objective.
5. Test Hint Mode as the default with a small student group rather than changing
   it permanently without evidence.
6. Measure answer accuracy, hint use, time on task, and student preference.

Verification:

- Compare plotted intercepts and roots with symbolic results.
- Test keyboard access, labels, contrast, mobile layout, and screen-reader text.
- Conduct a small usability test with students.

Potential risks:

- Decorative graphs can distract without improving understanding.
- A Hint Mode default may frustrate students who only want answer checking.

## Recommended Order

1. Secure parser and student data boundaries.
2. Isolate tests and add CI.
3. Implement true skill-targeted adaptation.
4. Build structured misconception and hint-ladder support.
5. Move feedback and learning events into transactional persistence.
6. Consolidate duplicate math routing incrementally.
7. Add valid analytics and small educational studies.
8. Add graph visuals after the event model can measure their effect.

## Immediate Next Task

The next implementation task should be a safe input boundary plus isolated test
database. These changes protect the public deployment and make every later
refactor safer. They should be completed before adding graphs or expanding the
curriculum.
