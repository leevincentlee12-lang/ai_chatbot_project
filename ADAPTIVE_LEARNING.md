# Adaptive Learning State

The app now separates browser identity from learning data:

1. Flask gives each browser an anonymous `user_id`.
2. The browser keeps only that `user_id` in its session cookie.
3. `core/state_store.py` stores the actual learning state in SQLite.
4. `core/progression.py` exposes beginner-friendly functions used by the rest
   of the app.

This makes the project behave more like a real tutoring platform because each
visitor has separate progress instead of sharing one global Python dictionary.

## What Is Stored

- Current topic: the latest active topic, such as `Linear Equations`.
- Recent questions: the latest questions asked by that browser session.
- Skill progression: score and attempt count per skill.
- Difficulty level: the adaptive level used when generating practice problems.
- Mistake history: incorrect answers, likely issue, expected answer, and skill.
- Basic stats: questions asked, problems attempted, correct answers, and lessons
  completed.

## File Structure

```text
core/
  progression.py   # learning-state API used by app.py and engines
  state_store.py   # SQLite persistence layer

app.py             # creates browser user_id and passes it to the backend
instance/          # local SQLite database folder, ignored by Git
```

## Storage Choice

### Flask Sessions

Use Flask sessions for identity only.

Good for:

- Remembering which anonymous browser is making the request.
- Keeping the app beginner-friendly.

Not good for:

- Storing full skill history.
- Storing lots of recent questions.
- Storing mistake history.

Reason: Flask's default session is cookie-based, so large or sensitive learning
state should not live there.

### SQLite

Use SQLite for this stage.

Good for:

- Beginner-friendly persistence.
- Real database tables without extra dependencies.
- Per-user progress, recent questions, steps, guided sessions, and mistakes.
- Local development and school demos.

Limit:

- On Render's free web service filesystem, local database files should be
  treated as temporary across restarts and redeploys unless you configure
  persistent storage.

### JSON Storage

Avoid JSON for learning state.

Good for:

- Tiny config files.
- Simple examples.

Not good for:

- Multiple users writing at the same time.
- Querying progress by topic or skill.
- Avoiding file corruption when two requests write together.

## Current Recommendation

Use:

```text
Flask session cookie: anonymous user_id only
SQLite: learning state
JSON: config/demo feedback only
```

The next production step would be moving SQLite/feedback data into Postgres,
but SQLite is the right beginner-friendly improvement now.

## API Endpoint

The app exposes the current user's learning state at:

```text
/learning-state
```

It returns:

```text
current_topic
recent_questions
skill_progression
difficulty_level
correct_streak
mistake_history
stats
```
