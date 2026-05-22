AI Chatbot Project
==================

Quick start
-----------

1. Create a Python 3.11 virtual environment (recommended).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run the test suite:

```powershell
python -m pytest -q
```

Usage
-----

This project exposes a legacy helper `answer_question(question, mode=None)` in `homework_helper.py`.
Examples (from Python):

```python
from homework_helper import answer_question
print(answer_question('solve x + y = 9 and x - y = 3', mode='direct'))
print(answer_question('show elimination method for 2x + y = 11 and x - y = 1', mode='step-by-step'))
print(answer_question('find x if sin 35 = x/12', mode='direct'))
```

What I changed
--------------
- Improved algebra detection in `core/classifier.py` to accept short cues like "solve"/"find" when accompanied by variables or numbers.
- Added support for simple trig equations in `engine/math_engine.py` (degree→radian conversion for numeric angles).
- Improved parsing of simultaneous-equation prompts so natural language like "show elimination method for ..." parses correctly.

Notes
-----
- I converted `requirements.txt` to UTF-8 to avoid encoding issues when installing.
- The full test suite passes locally: `32 passed`.

Next steps (optional)
---------------------
- Review the changes and commit them to your repository.
- If you want stricter scope, we can revert trig support or expand it to more trig scenarios.
