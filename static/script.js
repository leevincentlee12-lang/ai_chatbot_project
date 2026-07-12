const messagesDiv = document.getElementById("messages");
const questionInput = document.getElementById("question");
const askButton = document.getElementById("ask");
const modeSelect = document.getElementById("modeSelect");
const analyticsBox = document.getElementById("analyticsBox");
const feedbackBox = document.getElementById("feedbackBox");
const lessonGrid = document.getElementById("lessonGrid");
const lessonLibraryButton = document.getElementById("open-lesson-library");
const graphEquationInput = document.getElementById("graphEquation");
const plotGraphButton = document.getElementById("plotGraph");
const graphSvg = document.getElementById("graphSvg");
const graphEquationLabel = document.getElementById("graphEquationLabel");
const graphSummary = document.getElementById("graphSummary");
const graphFeatureList = document.getElementById("graphFeatureList");
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

let lastQuestion = "";
let loadingTimer = null;

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
  ["algebra focus", "Algebra Focus"],
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

  loadingTimer = window.setTimeout(() => {
    const loadingElement = document.getElementById("loading");
    if (loadingElement) {
      loadingElement.textContent = "Platform: Still preparing guidance. The first request can take longer while the server starts.";
    }
  }, 7000);
}

function removeLoading() {
  if (loadingTimer) {
    window.clearTimeout(loadingTimer);
    loadingTimer = null;
  }

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

function getPromptMode(prompt) {
  const text = String(prompt || "").toLowerCase();
  if (text.includes("hint")) {
    return "hint";
  }
  if (text.includes("working") || text.includes("step")) {
    return "step-by-step";
  }
  if (text.includes("direct")) {
    return "direct";
  }
  return modeSelect ? modeSelect.value : "";
}

function extractEquationText(question) {
  const text = String(question || "").trim();
  if (!text || !text.includes("=")) {
    return "";
  }

  return text
    .replace(/^\s*(solve(?:\s+for\s+x)?|find\s+x(?:\s+(?:in|if|when))?|what\s+is\s+x(?:\s+(?:if|in|when))?|show\s+the\s+full\s+working\s+for|give\s+me\s+a\s+hint\s+for)\s*[:,-]?\s*/i, "")
    .trim();
}

function getMathSupportPrompts(data, originalQuestion, currentMode = "") {
  if ((data.subject || "").toLowerCase() !== "math") {
    return [];
  }

  const equation = extractEquationText(originalQuestion);
  if (!equation || !/[xy]/i.test(equation)) {
    return [];
  }

  const prompts = [];
  prompts.push({
    label: currentMode === "hint" ? "Ask for another hint" : "Ask for a hint",
    prompt: `give me a hint for ${equation}`,
    mode: "hint",
  });

  if (currentMode !== "step-by-step") {
    prompts.push({
      label: "Show step-by-step working",
      prompt: `show the full working for ${equation}`,
      mode: "step-by-step",
    });
  }
  return prompts;
}

function appendStructuredBotMessage(data, originalQuestion, currentMode = "") {
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

  const supportPrompts = getMathSupportPrompts(data, originalQuestion, currentMode);
  if (supportPrompts.length > 0) {
    appendActionChips(supportPrompts, "Need more support?");
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

  const seen = new Set();

  prompts.forEach((item) => {
    const prompt = typeof item === "string" ? item : item.prompt;
    const chipLabel = typeof item === "string" ? item : item.label;
    const chipMode = typeof item === "string"
      ? getPromptMode(prompt)
      : (item.mode || getPromptMode(prompt));
    const key = `${chipLabel || prompt}|${chipMode}`;

    if (!prompt || seen.has(key)) {
      return;
    }
    seen.add(key);

    const button = document.createElement("button");
    button.className = "followup-chip";
    button.type = "button";
    button.textContent = chipLabel || prompt;
    button.addEventListener("click", () => askQuestionWithText(
      prompt,
      chipMode,
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
    appendStructuredBotMessage(data, trimmedQuestion, mode);
    loadStudentDashboard();
  } catch (error) {
    removeLoading();
    appendMessage(error.message || "Unable to reach the backend.", "bot");
  } finally {
    askButton.disabled = false;
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

function svgElement(name, attributes = {}) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, String(value));
  });
  return element;
}

function scalePoint(point, bounds, width, height, padding) {
  const [xMin, xMax] = bounds.x;
  const [yMin, yMax] = bounds.y;
  const xRatio = (point.x - xMin) / (xMax - xMin);
  const yRatio = (point.y - yMin) / (yMax - yMin);
  return {
    x: padding + xRatio * (width - padding * 2),
    y: height - padding - yRatio * (height - padding * 2),
  };
}

function renderGraph(data) {
  if (!graphSvg) {
    return;
  }

  const width = 720;
  const height = 420;
  const padding = 42;
  const bounds = {
    x: data.x_range || [-5, 5],
    y: data.y_range || [-10, 10],
  };

  graphSvg.innerHTML = "";
  graphSvg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const background = svgElement("rect", {
    x: 0,
    y: 0,
    width,
    height,
    class: "graph-background",
  });
  graphSvg.appendChild(background);

  for (let value = -5; value <= 5; value += 1) {
    const vertical = scalePoint({ x: value, y: bounds.y[0] }, bounds, width, height, padding);
    graphSvg.appendChild(svgElement("line", {
      x1: vertical.x,
      y1: padding,
      x2: vertical.x,
      y2: height - padding,
      class: "graph-grid-line",
    }));
  }

  const yStart = Math.ceil(bounds.y[0]);
  const yEnd = Math.floor(bounds.y[1]);
  const yStep = Math.max(1, Math.ceil((yEnd - yStart) / 8));
  for (let value = yStart; value <= yEnd; value += yStep) {
    const horizontal = scalePoint({ x: bounds.x[0], y: value }, bounds, width, height, padding);
    graphSvg.appendChild(svgElement("line", {
      x1: padding,
      y1: horizontal.y,
      x2: width - padding,
      y2: horizontal.y,
      class: "graph-grid-line",
    }));
  }

  const xAxis = scalePoint({ x: bounds.x[0], y: 0 }, bounds, width, height, padding);
  graphSvg.appendChild(svgElement("line", {
    x1: padding,
    y1: xAxis.y,
    x2: width - padding,
    y2: xAxis.y,
    class: "graph-axis-line",
  }));

  const yAxis = scalePoint({ x: 0, y: bounds.y[0] }, bounds, width, height, padding);
  graphSvg.appendChild(svgElement("line", {
    x1: yAxis.x,
    y1: padding,
    x2: yAxis.x,
    y2: height - padding,
    class: "graph-axis-line",
  }));

  const path = (data.points || [])
    .map((point, index) => {
      const scaled = scalePoint(point, bounds, width, height, padding);
      return `${index === 0 ? "M" : "L"} ${scaled.x.toFixed(2)} ${scaled.y.toFixed(2)}`;
    })
    .join(" ");

  graphSvg.appendChild(svgElement("path", {
    d: path,
    class: "graph-function-path",
  }));
}

function renderGraphFeatures(data) {
  if (!graphEquationLabel || !graphSummary || !graphFeatureList) {
    return;
  }

  const features = data.features || {};
  const entries = [];

  if (data.kind === "linear") {
    entries.push(["Gradient", features.gradient]);
    entries.push(["Y-intercept", features.y_intercept]);
  } else if (data.kind === "quadratic") {
    entries.push(["Vertex", features.vertex ? `(${features.vertex.x}, ${features.vertex.y})` : "Not available"]);
    entries.push(["Y-intercept", features.y_intercept]);
  }

  entries.push([
    "X-intercepts",
    Array.isArray(features.x_intercepts) && features.x_intercepts.length > 0
      ? features.x_intercepts.join(", ")
      : "None in the real-number graph",
  ]);

  graphEquationLabel.textContent = data.equation || "Supported function";
  graphSummary.textContent = features.summary || "Graph data loaded.";
  graphFeatureList.innerHTML = "";

  entries.forEach(([label, value]) => {
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = value || "Not available";
    graphFeatureList.appendChild(term);
    graphFeatureList.appendChild(description);
  });
}

async function plotGraph() {
  if (!graphEquationInput || !graphSvg) {
    return;
  }

  const equation = graphEquationInput.value.trim();
  if (!equation) {
    graphSummary.textContent = "Enter a function such as y = 2x + 3.";
    return;
  }

  plotGraphButton.disabled = true;
  graphSummary.textContent = "Plotting function...";

  try {
    const data = await fetchJson("/graph-data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equation }),
    });
    renderGraph(data);
    renderGraphFeatures(data);
  } catch (error) {
    graphSvg.innerHTML = "";
    graphEquationLabel.textContent = "Graph unavailable";
    graphSummary.textContent = error.message || "Unable to plot that function.";
    graphFeatureList.innerHTML = "";
  } finally {
    plotGraphButton.disabled = false;
  }
}

askButton.addEventListener("click", askQuestion);
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    askQuestion();
  }
});

bindClick("refresh-dashboard", loadStudentDashboard);
bindClick("show-progress", showProgress);
bindClick("show-skills", showSkills);
bindClick("show-analytics", getAnalytics);
bindClick("view-feedback", viewFeedback);
lessonLibraryButton.addEventListener("click", () => {
  lessonGrid.scrollIntoView({ behavior: "smooth", block: "start" });
});
if (plotGraphButton) {
  plotGraphButton.addEventListener("click", plotGraph);
}
if (graphEquationInput) {
  graphEquationInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      plotGraph();
    }
  });
}

document.querySelectorAll("[data-suggest]").forEach((button) => {
  button.addEventListener("click", () => applySuggestion(button.dataset.suggest));
});

plotGraph();
loadLessonCatalog();
loadStudentDashboard();
