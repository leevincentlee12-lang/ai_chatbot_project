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

let currentProblem = null;
let currentPracticePrompts = [];
let lastQuestion = "";

function appendMessage(text, who = "bot") {
  const element = document.createElement("div");
  element.className = `message ${who === "user" ? "user" : "bot"}`;
  element.textContent = `${who === "user" ? "You: " : "AI: "}${text}`;
  messagesDiv.appendChild(element);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function appendLoading() {
  const element = document.createElement("div");
  element.className = "message bot";
  element.id = "loading";
  element.innerHTML = 'AI: <span class="dots">Thinking</span>';
  messagesDiv.appendChild(element);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeLoading() {
  const element = document.getElementById("loading");
  if (element) {
    element.remove();
  }
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

  const answer = document.createElement("div");
  answer.className = "answer-block";
  answer.textContent = data.answer || "No answer available.";

  container.appendChild(subject);
  container.appendChild(topic);
  container.appendChild(answer);
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
  } catch (error) {
    practiceProblemBox.textContent = error.message || "Unable to load practice problem.";
  }
}

async function showProgress() {
  try {
    const data = await fetchJson("/progress");
    appendMessage(
      `Questions asked: ${data.questions_asked}\n` +
        `Problems attempted: ${data.attempted}\n` +
        `Correct answers: ${data.correct}\n` +
        `Accuracy: ${data.accuracy}%\n` +
        `Lessons opened: ${data.lessons_completed}`,
      "bot",
    );
  } catch (error) {
    appendMessage(error.message || "Unable to load progress.", "bot");
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
      return `${skill}: ${details.score}/100 (${details.attempts} attempts)`;
    });

    appendMessage(lines.join("\n") || "No skill data available.", "bot");
  } catch (error) {
    appendMessage(error.message || "Unable to load skills.", "bot");
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

  const answer = document.createElement("div");
  answer.className = "answer-block";
  answer.textContent = data.details || data.result || "No feedback available.";
  container.appendChild(answer);
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

    const learnButton = document.createElement("button");
    learnButton.className = "primary-button";
    learnButton.type = "button";
    learnButton.textContent = `Learn ${lesson.button_label}`;
    learnButton.addEventListener("click", () => getLesson(lesson.topic));

    const promptButton = document.createElement("button");
    promptButton.className = "ghost-button";
    promptButton.type = "button";
    promptButton.textContent = "Use prompt";
    promptButton.addEventListener("click", () => applySuggestion(lesson.starter_prompt));

    actions.appendChild(learnButton);
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

askButton.addEventListener("click", askQuestion);
questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    askQuestion();
  }
});

document.getElementById("submit-answer").addEventListener("click", submitAnswer);
document.getElementById("practice-easy").addEventListener("click", () => getPractice(1));
document.getElementById("practice-medium").addEventListener("click", () => getPractice(2));
document.getElementById("practice-hard").addEventListener("click", () => getPractice(3));
document.getElementById("show-progress").addEventListener("click", showProgress);
document.getElementById("show-skills").addEventListener("click", showSkills);
document.getElementById("show-analytics").addEventListener("click", getAnalytics);
document.getElementById("view-feedback").addEventListener("click", viewFeedback);
lessonLibraryButton.addEventListener("click", () => {
  lessonGrid.scrollIntoView({ behavior: "smooth", block: "start" });
});

document.querySelectorAll("[data-suggest]").forEach((button) => {
  button.addEventListener("click", () => applySuggestion(button.dataset.suggest));
});

loadLessonCatalog();
