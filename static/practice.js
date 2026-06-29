const problemBox = document.getElementById("practiceModeProblem");
const workingInput = document.getElementById("practiceModeWorking");
const answerInput = document.getElementById("practiceModeAnswer");
const checkButton = document.getElementById("practiceModeCheck");
const checkWorkingButton = document.getElementById("practiceModeCheckWorking");
const clearWorkingButton = document.getElementById("practiceModeClearWorking");
const retryButton = document.getElementById("practiceModeRetry");
const newProblemButton = document.getElementById("practiceModeNew");
const feedbackBox = document.getElementById("practiceModeFeedback");

const dashboard = {
  attempted: document.getElementById("practiceDashAttempted"),
  correct: document.getElementById("practiceDashCorrect"),
  accuracy: document.getElementById("practiceDashAccuracy"),
  streak: document.getElementById("practiceDashStreak"),
  difficulty: document.getElementById("practiceDashDifficulty"),
  weakest: document.getElementById("practiceDashWeakest"),
};

const SECTION_LABELS = new Map([
  ["answer", "Answer"],
  ["result", "Answer"],
  ["method", "Method"],
  ["how to fix it", "Method"],
  ["why", "Why"],
  ["why it works", "Why"],
  ["check", "Check"],
  ["likely issue", "Check"],
  ["mastery", "Progress"],
  ["recommended practice", "Next Step"],
  ["next step", "Next Step"],
]);

let currentProblem = null;
let currentLevel = 1;
let lastResult = null;

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.answer || data.result || "Request failed.");
  }

  return data;
}

function formatSkillLabel(value) {
  if (!value) {
    return "Not available";
  }

  return String(value)
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function findWeakestSkill(skills = {}) {
  const entries = Object.entries(skills);
  if (entries.length === 0) {
    return "Not available";
  }

  const [skillName] = entries.reduce((weakest, current) => {
    const weakestScore = Number(weakest[1]?.score ?? 0);
    const currentScore = Number(current[1]?.score ?? 0);
    return currentScore < weakestScore ? current : weakest;
  });
  return formatSkillLabel(skillName);
}

function setDashboardValue(key, value) {
  if (dashboard[key]) {
    dashboard[key].textContent = value;
  }
}

function normaliseHeading(line) {
  return SECTION_LABELS.get(String(line || "").trim().toLowerCase()) || null;
}

function parseSections(text) {
  const rawText = String(text || "").trim();
  if (!rawText) {
    return [{ title: "Answer", body: "No feedback available." }];
  }

  const sections = [];
  let current = null;

  rawText.split(/\r?\n/).forEach((line) => {
    const heading = normaliseHeading(line);
    if (heading) {
      if (current && current.body.length > 0) {
        sections.push({
          title: current.title,
          body: current.body.join("\n").trim(),
        });
      }
      current = { title: heading, body: [] };
      return;
    }

    if (!current) {
      current = { title: "Answer", body: [] };
    }
    current.body.push(line);
  });

  if (current && current.body.length > 0) {
    sections.push({
      title: current.title,
      body: current.body.join("\n").trim(),
    });
  }

  const cleaned = sections.filter((section) => section.body);
  return cleaned.length > 0 ? cleaned : [{ title: "Answer", body: rawText }];
}

function renderSections(text) {
  const wrapper = document.createElement("div");
  wrapper.className = "response-sections";

  parseSections(text).forEach((section) => {
    const card = document.createElement("section");
    card.className = `response-section ${section.title.toLowerCase().replace(/\s+/g, "-")}`;

    const heading = document.createElement("h4");
    heading.textContent = section.title;

    const body = document.createElement("div");
    body.className = "response-section-body";
    body.textContent = section.body;

    card.appendChild(heading);
    card.appendChild(body);
    wrapper.appendChild(card);
  });

  return wrapper;
}

function setFeedback(text, status = "") {
  feedbackBox.className = `practice-feedback ${status}`.trim();
  feedbackBox.innerHTML = "";
  feedbackBox.appendChild(renderSections(text));
}

function setProblem(data) {
  currentProblem = data.problem;
  lastResult = null;
  const reason = data.adaptive_reason
    ? `\nFocus: ${data.adaptive_focus || formatSkillLabel(data.skill)}\nReason: ${data.adaptive_reason}`
    : "";
  problemBox.textContent = `${data.difficulty} ${formatSkillLabel(data.skill)}\n${data.problem}${reason}`;
  workingInput.value = "";
  answerInput.value = "";
  answerInput.disabled = false;
  checkButton.disabled = false;
  setFeedback("Use the working space if needed, then check your answer.", "");
  workingInput.focus();
}

async function generateProblem(level = currentLevel) {
  currentLevel = Number(level) || 1;
  problemBox.textContent = "Generating problem...";
  try {
    const data = await fetchJson(`/practice/${currentLevel}`);
    setProblem(data);
    await loadProgress();
  } catch (error) {
    problemBox.textContent = error.message || "Unable to generate a practice problem.";
  }
}

async function checkAnswer() {
  if (!currentProblem) {
    setFeedback("Generate a problem before checking an answer.", "error");
    return;
  }

  const answer = answerInput.value.trim();
  if (!answer) {
    setFeedback("Enter an answer before checking.", "error");
    answerInput.focus();
    return;
  }

  checkButton.disabled = true;
  setFeedback("Checking your answer...", "");

  try {
    const data = await fetchJson("/check-answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        equation: currentProblem,
        answer,
      }),
    });

    lastResult = data;
    setFeedback(data.details || data.result || "No feedback available.", data.status || "");
    checkButton.disabled = data.status === "correct";
    await loadProgress();
  } catch (error) {
    checkButton.disabled = false;
    setFeedback(error.message || "Unable to check answer.", "error");
  }
}

function getWorkingSteps() {
  return workingInput.value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

async function checkWorking() {
  const workingSteps = getWorkingSteps();
  if (workingSteps.length === 0) {
    setFeedback("Enter at least one working line before checking.", "error");
    workingInput.focus();
    return;
  }

  const steps = [...workingSteps];
  if (currentProblem && steps[0] !== currentProblem) {
    steps.unshift(currentProblem);
  }

  checkWorkingButton.disabled = true;
  setFeedback("Checking your working...", "");

  try {
    const data = await fetchJson("/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ steps }),
    });

    const result = data.result || "No working feedback available.";
    const status = result.includes("All transformations") ? "correct" : "error";
    setFeedback(result, status);
  } catch (error) {
    setFeedback(error.message || "Unable to check working.", "error");
  } finally {
    checkWorkingButton.disabled = false;
  }
}

function clearWorking() {
  workingInput.value = "";
  setFeedback("Working space cleared.", "");
  workingInput.focus();
}

function retryProblem() {
  if (!currentProblem) {
    setFeedback("Generate a problem before retrying.", "error");
    return;
  }

  workingInput.value = "";
  answerInput.value = "";
  answerInput.disabled = false;
  checkButton.disabled = false;
  lastResult = null;
  setFeedback("Try the same problem again. Your next check will update progress.", "");
  workingInput.focus();
}

async function loadProgress() {
  try {
    const state = await fetchJson("/learning-state");
    const stats = state.stats || {};
    const attempted = Number(stats.problems_attempted || 0);
    const correct = Number(stats.correct_answers || 0);
    const accuracy = attempted > 0
      ? Math.round((correct / attempted) * 10000) / 100
      : 0;

    setDashboardValue("attempted", String(attempted));
    setDashboardValue("correct", String(correct));
    setDashboardValue("accuracy", `${accuracy}%`);
    setDashboardValue("streak", String(state.correct_streak ?? 0));
    setDashboardValue("difficulty", `Level ${state.difficulty_level ?? 1}`);
    setDashboardValue("weakest", findWeakestSkill(state.skill_progression || {}));
  } catch (error) {
    setDashboardValue("attempted", "Unavailable");
    setDashboardValue("correct", "Unavailable");
    setDashboardValue("accuracy", "Unavailable");
    setDashboardValue("streak", "Unavailable");
    setDashboardValue("difficulty", "Unavailable");
    setDashboardValue("weakest", "Unavailable");
  }
}

document.querySelectorAll("[data-level]").forEach((button) => {
  button.addEventListener("click", () => generateProblem(button.dataset.level));
});

checkButton.addEventListener("click", checkAnswer);
checkWorkingButton.addEventListener("click", checkWorking);
clearWorkingButton.addEventListener("click", clearWorking);
retryButton.addEventListener("click", retryProblem);
newProblemButton.addEventListener("click", () => generateProblem(currentLevel));
answerInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    checkAnswer();
  }
});

loadProgress();
