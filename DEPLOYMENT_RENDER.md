# Deploying The Flask Homework Helper On Render

This guide assumes you are a beginner and you want to deploy the project
publicly using GitHub Desktop and Render.

## What You Need

1. A GitHub account.
2. GitHub Desktop installed.
3. A Render account.
4. This project folder on your computer.

Your project already has the important deployment files:

- `app.py`
- `requirements.txt`
- `Procfile`
- `.python-version`

## Step 1: Test The App Locally

Open PowerShell in the project folder:

```powershell
cd C:\Users\User\ai_chatbot_project
python -m pip install -r requirements.txt
python -m unittest
python app.py
```

Open this in your browser:

```text
http://localhost:5000
```

Stop the local server with `Ctrl+C` in PowerShell.

## Step 2: Open The Project In GitHub Desktop

1. Open GitHub Desktop.
2. Click `File`.
3. Click `Add local repository`.
4. Click `Choose`.
5. Select:

```text
C:\Users\User\ai_chatbot_project
```

6. Click `Add repository`.

If GitHub Desktop says this folder is not a Git repository, choose the option to
create a repository from the existing folder.

## Step 3: Commit Your Changes

1. In GitHub Desktop, look at the left panel.
2. You should see changed files.
3. In the `Summary` box, type:

```text
Refactor modular architecture and add deployment docs
```

4. Click `Commit to main`.

## Step 4: Publish To GitHub

1. In GitHub Desktop, click `Publish repository`.
2. Repository name:

```text
ai-chatbot-homework-helper
```

3. Description:

```text
Modular Flask homework helper for high school study support
```

4. If you want the school/application reviewers to see the code, untick
   `Keep this code private`.
5. Click `Publish Repository`.

Now your code is on GitHub.

## Step 5: Create A Render Web Service

1. Go to:

```text
https://dashboard.render.com
```

2. Sign in.
3. Click `New`.
4. Click `Web Service`.
5. Connect your GitHub account if Render asks.
6. Select your repository:

```text
ai-chatbot-homework-helper
```

7. Click `Connect`.

## Step 6: Use These Render Settings

Use these exact values:

```text
Name: ai-chatbot-homework-helper
Language: Python 3
Branch: main
Root Directory: leave blank
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
Instance Type: Free
```

Environment variables:

```text
PYTHON_VERSION = 3.11.9
```

You can also leave environment variables empty because `.python-version` is
already committed, but setting `PYTHON_VERSION` makes the version explicit in
the Render dashboard.

## Step 7: Deploy

1. Click `Create Web Service`.
2. Wait for Render to build the app.
3. Watch the logs.
4. If the deploy succeeds, Render will show `Live`.
5. Click the public `.onrender.com` URL.

Your deployed URL will look similar to:

```text
https://ai-chatbot-homework-helper.onrender.com
```

## Step 8: Test The Live App

Open the Render URL and try:

```text
solve 2x + 4 = 10
```

Select direct mode if the UI gives you a mode option.

Also test these routes manually:

```text
/lessons
/practice/1
/progress
```

Example:

```text
https://ai-chatbot-homework-helper.onrender.com/lessons
```

## Step 9: Update The App Later

Every time you make a change:

1. Test locally:

```powershell
python -m unittest
```

2. Open GitHub Desktop.
3. Review changed files.
4. Type a clear summary.
5. Click `Commit to main`.
6. Click `Push origin`.

Render will automatically redeploy from the GitHub `main` branch.

## If Deployment Fails

Check the Render logs first.

Common fixes:

- `ModuleNotFoundError`: make sure the package is listed in `requirements.txt`.
- `No module named app`: make sure `app.py` is in the project root.
- `Application failed to bind to port`: make sure the start command uses:

```text
gunicorn app:app --bind 0.0.0.0:$PORT
```

- Python version error: add or check:

```text
PYTHON_VERSION = 3.11.9
```

## Important Limitation

Feedback logs are stored in `feedback_log.json`. On Render, local files are not
a strong long-term database. The app is fine for a demo, but if real students
use it, move feedback and progress into a database.
