const messagesDiv = document.getElementById("messages");
const questionInput = document.getElementById("question");
const askButton = document.getElementById("ask");
const modeSelect = document.getElementById("modeSelect");
const studentAnswerInput = document.getElementById("studentAnswer");
const practiceProblemBox = document.getElementById("practiceProblem");
const analyticsBox = document.getElementById("analyticsBox");
const feedbackBox = document.getElementById("feedbackBox");
const lessonGrid = document.getElementById("lessonGrid");
const lessonLibraryButton = document.getElementById("open-lesson-library");
const dashboard = {
  questions: document.getElementById("dash-questions"),
  attempted: document.getElementById("dash-attempted"),
  correct: document.getElementById("dash-correct"),
  accuracy: document.getElementById("dash-accuracy"),
  difficulty: document.getElementById("dash-difficulty"),
  topic: document.getElementById("dash-topic"),
  weakest: document.getElementById("dash-weakest"),
  streak: document.getElementById("dash-streak"),
};

let currentProblem = null;
let currentPracticePrompts = [];
let lastQuestion = "";

const RESPONSE_SECTION_LABELS = new Map([
  ["answer", "Answer"],
  ["result", "Answer"],
  ["method", "Method"],
  ["how to fix it", "Method"],
  ["why", "Why"],
  ["why it works", "Why"],
  ["check", "Check"],
  ["likely issue", "Check"],
  ["mastery", "Progress"],
  ["next step", "Next Step"],
]);

function appendMessage(text, who = "bot") {
  const element = document.createElement("div");
  element.className = `message ${who === "user" ? "user" : "bot"}`;
  element.textContent = `${who === "user" ? "You: " : "Platform: "}${text}`;
  messagesDiv.appendChild(element);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function appendLoading() {
  const element = document.createElement("div");
  element.className = "message bot";
  element.id = "loading";
  element.innerHTML = 'Platform: <span class="dots">Preparing guidance</span>';
  messagesDiv.appendChild(element);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeLoading() {
  const element = document.getElementById("loading");
  if (element) {
    element.remove();
  }
}

function normaliseSectionHeading(line) {
  return RESPONSE_SECTION_LABELS.get(String(line || "").trim().toLowerCase()) || null;
}

function parseResponseSections(text) {
  const rawText = String(text || "").trim();
  if (!rawText) {
    return [{ title: "Answer", body: "No answer available." }];
  }

  const sections = [];
  let current = null;

  rawText.split(/\r?\n/).forEach((line) => {
    const heading = normaliseSectionHeading(line);
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

function renderEducationalResponse(text) {
  const wrapper = document.createElement("div");
  wrapper.className = "response-sections";

  parseResponseSections(text).forEach((section) => {
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

function appendStructuredBotMessage(data, originalQuestion) {
  const container = document.createElement("div");
  container.className = "message bot";

  const subject = document.createElement("div");
  subject.className = "subject-badge";
  subject.textContent = data.subject || "General";

  const topic = document.createElement("div");
  topic.className = "topic-line";
  topic.textContent = data.topic || "";

  container.appendChild(subject);
  container.appendChild(topic);
  container.appendChild(renderEducationalResponse(data.answer));
  messagesDiv.appendChild(container);

  if (Array.isArray(data.followups) && data.followups.length > 0) {
    appendActionChips(data.followups, "Try next");
  }
  appendFeedbackBlock(data, originalQuestion);
}

function appendLessonMessage(data) {
  const container = document.createElement("div");
  container.className = "message bot";

  const badge = document.createElement("div");
  badge.className = "subject-badge";
  badge.textContent = "Lesson";

  const topic = document.createElement("div");
  topic.className = "topic-line";
  topic.textContent = `${data.title} | ${data.level} | ${data.strand}`;

  const lessonText = document.createElement("div");
  lessonText.className = "answer-block";
  lessonText.textContent = data.display_text || "No lesson content available.";

  container.appendChild(badge);
  container.appendChild(topic);
  container.appendChild(lessonText);
  messagesDiv.appendChild(container);

  if (Array.isArray(data.practice_prompts) && data.practice_prompts.length > 0) {
    appendActionChips(data.practice_prompts, "Practice prompts");
  }

  if (Array.isArray(data.related_lessons) && data.related_lessons.length > 0) {
    appendActionChips(
      data.related_lessons.map((lesson) => `learn ${lesson.button_label.toLowerCase()}`),
      "Related lessons",
    );
  }
}

function appendActionChips(prompts, label = "Suggested prompts") {
  const wrapper = document.createElement("div");
  wrapper.className = "followup-block";

  const title = document.createElement("div");
  title.className = "followup-title";
  title.textContent = label;
  wrapper.appendChild(title);

  prompts.forEach((prompt) => {
    const button = document.createElement("button");
    button.className = "followup-chip";
    button.type = "button";
    button.textContent = prompt;
    button.addEventListener("click", () => askQuestionWithText(
      prompt,
      modeSelect ? modeSelect.value : "",
    ));
    wrapper.appendChild(button);
  });

  messagesDiv.appendChild(wrapper);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function appendFeedbackBlock(data, originalQuestion) {
  const feedback = document.createElement("div");
  feedback.className = "feedback-block";

  const title = document.createElement("div");
  title.className = "feedback-title";
  title.textContent = "Rate this response";

  const rating = document.createElement("select");
  rating.className = "rating";

  ["", "1", "2", "3", "4", "5"].forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value || "Select";
    rating.appendChild(option);
  });

  const button = document.createElement("button");
  button.className = "ghost-button";
  button.type = "button";
  button.textContent = "Submit";

  const status = document.createElement("span");
  status.className = "status";

  button.addEventListener("click", async () => {
    if (!rating.value) {
      status.textContent = "Select a rating first.";
      return;
    }

    await fetchJson("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: originalQuestion,
        subject: data.subject,
        topic: data.topic,
        rating: rating.value,
      }),
    });

    status.textContent = "Saved.";
  });

  feedback.appendChild(title);
  feedback.appendChild(rating);
  feedback.appendChild(button);
  feedback.appendChild(status);
  messagesDiv.appendChild(feedback);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = data.answer || data.result || "Request failed.";
    throw new Error(error);
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

function normaliseStats(progress = {}, state = {}) {
  const stateStats = state.stats || {};
  const attempted = Number(
    progress.attempted ?? stateStats.problems_attempted ?? 0,
  );
  const correct = Number(
    progress.correct ?? stateStats.correct_answers ?? 0,
  );
  const accuracy = Number.isFinite(Number(progress.accuracy))
    ? Number(progress.accuracy)
    : attempted > 0
      ? Math.round((correct / attempted) * 10000) / 100
      : 0;

  return {
    questions: Number(
      progress.questions_asked ?? stateStats.questions_asked ?? 0,
    ),
    attempted,
    correct,
    accuracy,
  };
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

function updateStudentDashboard({ progress = {}, skills = {}, state = {} }) {
  const stats = normaliseStats(progress, state);
  const stateSkills = state.skill_progression || skills;
  const difficulty = state.difficulty_level ?? progress.difficulty_level;
  const topic = state.current_topic ?? progress.current_topic;
  const streak = state.correct_streak ?? progress.correct_streak;

  setDashboardValue("questions", String(stats.questions));
  setDashboardValue("attempted", String(stats.attempted));
  setDashboardValue("correct", String(stats.correct));
  setDashboardValue("accuracy", `${stats.accuracy}%`);
  setDashboardValue(
    "difficulty",
    difficulty === undefined || difficulty === null
      ? "Not available"
      : `Level ${difficulty}`,
  );
  setDashboardValue("topic", formatSkillLabel(topic));
  setDashboardValue("weakest", findWeakestSkill(stateSkills));
  setDashboardValue(
    "streak",
    streak === undefined || streak === null ? "Not available" : String(streak),
  );
}

async function loadStudentDashboard() {
  try {
    const state = await fetchJson("/learning-state");
    updateStudentDashboard({ state });
    return;
  } catch (error) {
    // Older deployments may not expose /learning-state yet. Fall back to the
    // existing progress and skill endpoints without inventing missing fields.
  }

  try {
    const [progress, skills] = await Promise.all([
      fetchJson("/progress"),
      fetchJson("/skills"),
    ]);
    updateStudentDashboard({ progress, skills });
  } catch (error) {
    setDashboardValue("topic", "Unable to load");
    setDashboardValue("weakest", "Unable to load");
  }
}

async function askQuestion() {
  const question = questionInput.value.trim();
  if (!question) {
    if (lastQuestion && modeSelect && modeSelect.value) {
      await askQuestionWithText(lastQuestion, modeSelect.value);
    }
    return;
  }

  await askQuestionWithText(question, modeSelect ? modeSelect.value : "");
}

async function askQuestionWithText(question, mode = "") {
  const trimmedQuestion = question.trim();
  if (!trimmedQuestion) {
    return;
  }

  lastQuestion = trimmedQuestion;

  appendMessage(trimmedQuestion, "user");
  questionInput.value = "";
  appendLoading();
  askButton.disabled = true;

  try {
    const data = await fetchJson("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: trimmedQuestion,
        mode,
      }),
    });

    removeLoading();
    appendStructuredBotMessage(data, trimmedQuestion);
    loadStudentDashboard();
  } catch (error) {
    removeLoading();
    appendMessage(error.message || "Unable to reach the backend.", "bot");
  } finally {
    askButton.disabled = false;
  }
}

async function getPractice(level) {
  try {
    const data = await fetchJson(`/practice/${level}`);
    currentProblem = data.problem;
    currentPracticePrompts = [
      `Show the full working for ${data.problem}`,
      `Give me a hint for ${data.problem}`,
      `Give me a similar problem to ${data.problem}`,
    ];
    practiceProblemBox.textContent =
      `${data.difficulty} ${data.skill.replace(/_/g, " ")} problem:\n${data.problem}`;
    studentAnswerInput.value = "";
    loadStudentDashboard();
  } catch (error) {
    practiceProblemBox.textContent = error.message || "Unable to load practice problem.";
  }
}

async function showProgress() {
  try {
    const data = await fetchJson("/progress");
    const summary =
      `Questions asked: ${data.questions_asked}\n` +
        `Problems attempted: ${data.attempted}\n` +
        `Correct answers: ${data.correct}\n` +
        `Accuracy: ${data.accuracy}%\n` +
        `Lessons opened: ${data.lessons_completed}`;
    analyticsBox.textContent = summary;
    loadStudentDashboard();
  } catch (error) {
    analyticsBox.textContent = error.message || "Unable to load progress.";
  }
}

async function getAnalytics() {
  try {
    const data = await fetchJson("/analytics");
    analyticsBox.textContent =
      `Total feedback entries: ${data.total_questions}\n` +
      `Average rating: ${data.average_rating}\n` +
      `Subject distribution: ${JSON.stringify(data.subject_distribution, null, 2)}`;
  } catch (error) {
    analyticsBox.textContent = error.message || "Unable to load analytics.";
  }
}

async function showSkills() {
  try {
    const data = await fetchJson("/skills");
    const lines = Object.entries(data).map(([skill, details]) => {
      return `${formatSkillLabel(skill)}: ${details.score}/100 (${details.attempts} attempts)`;
    });

    feedbackBox.textContent = lines.join("\n") || "No skill data available.";
    loadStudentDashboard();
  } catch (error) {
    feedbackBox.textContent = error.message || "Unable to load skills.";
  }
}

async function submitAnswer() {
  if (!currentProblem) {
    appendMessage("Generate a practice problem before submitting an answer.", "bot");
    return;
  }

  const answer = studentAnswerInput.value.trim();
  if (!answer) {
    appendMessage("Enter an answer before submitting.", "bot");
    return;
  }

  try {
    const data = await fetchJson("/check-answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        equation: currentProblem,
        answer,
      }),
    });

    appendStructuredPracticeFeedback(data);
    loadStudentDashboard();
  } catch (error) {
    appendMessage(error.message || "Unable to check answer.", "bot");
  }
}

function appendStructuredPracticeFeedback(data) {
  const container = document.createElement("div");
  container.className = `message bot ${data.status || ""}`.trim();

  if (data.headline) {
    const badge = document.createElement("div");
    badge.className = `subject-badge practice-${data.status || "neutral"}`;
    badge.textContent = data.headline;
    container.appendChild(badge);
  }

  container.appendChild(renderEducationalResponse(
    data.details || data.result || "No feedback available.",
  ));
  messagesDiv.appendChild(container);

  const prompts = Array.isArray(data.next_steps) && data.next_steps.length > 0
    ? data.next_steps
    : currentPracticePrompts;

  if (prompts.length > 0) {
    appendActionChips(prompts, "Practice follow-up");
  }
}

async function viewFeedback() {
  try {
    const data = await fetchJson("/analytics");
    feedbackBox.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    feedbackBox.textContent = error.message || "Unable to load feedback.";
  }
}

async function getLesson(topic) {
  try {
    const data = await fetchJson(`/lesson/${topic}`);
    appendLessonMessage(data);
    loadStudentDashboard();
  } catch (error) {
    appendMessage(error.message || "Unable to load lesson.", "bot");
  }
}

function renderLessonCatalog(lessons) {
  lessonGrid.innerHTML = "";

  lessons.forEach((lesson) => {
    const card = document.createElement("article");
    card.className = "lesson-card";

    const meta = document.createElement("div");
    meta.className = "lesson-meta";
    meta.textContent = `${lesson.strand} | ${lesson.level}`;

    const title = document.createElement("h3");
    title.textContent = lesson.title;

    const summary = document.createElement("p");
    summary.className = "lesson-summary";
    summary.textContent = lesson.summary;

    const actions = document.createElement("div");
    actions.className = "lesson-actions";

    const learnButton = document.createElement("a");
    learnButton.className = "primary-button";
    learnButton.href = `/lessons/${lesson.topic}`;
    learnButton.textContent = `Open ${lesson.button_label}`;

    const previewButton = document.createElement("button");
    previewButton.className = "ghost-button";
    previewButton.type = "button";
    previewButton.textContent = "Preview";
    previewButton.addEventListener("click", () => getLesson(lesson.topic));

    const promptButton = document.createElement("button");
    promptButton.className = "ghost-button";
    promptButton.type = "button";
    promptButton.textContent = "Use prompt";
    promptButton.addEventListener("click", () => applySuggestion(lesson.starter_prompt));

    actions.appendChild(learnButton);
    actions.appendChild(previewButton);
    actions.appendChild(promptButton);

    card.appendChild(meta);
    card.appendChild(title);
    card.appendChild(summary);
    card.appendChild(actions);
    lessonGrid.appendChild(card);
  });
}

async function loadLessonCatalog() {
  try {
    const data = await fetchJson("/lessons");
    renderLessonCatalog(data.lessons || []);
  } catch (error) {
    lessonGrid.innerHTML = "";
    const fallback = document.createElement("div");
    fallback.className = "status-card";
    fallback.textContent = error.message || "Unable to load lessons.";
    lessonGrid.appendChild(fallback);
  }
}

function applySuggestion(text) {
  questionInput.value = text;
  questionInput.focus();
}

function bindClick(id, handler) {
  const element = document.getElementById(id);
  if (element) {
    element.addEventListener("click", handler);
  }
}

askButton.addEventListener("click", askQuestion);
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    askQuestion();
  }
});

bindClick("submit-answer", submitAnswer);
bindClick("practice-easy", () => getPractice(1));
bindClick("practice-medium", () => getPractice(2));
bindClick("practice-hard", () => getPractice(3));
bindClick("refresh-dashboard", loadStudentDashboard);
bindClick("show-progress", showProgress);
bindClick("show-skills", showSkills);
bindClick("show-analytics", getAnalytics);
bindClick("view-feedback", viewFeedback);
lessonLibraryButton.addEventListener("click", () => {
  lessonGrid.scrollIntoView({ behavior: "smooth", block: "start" });
});

document.querySelectorAll("[data-suggest]").forEach((button) => {
  button.addEventListener("click", () => applySuggestion(button.dataset.suggest));
});

loadLessonCatalog();
loadStudentDashboard();
