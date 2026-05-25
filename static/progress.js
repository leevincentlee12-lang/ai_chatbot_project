const summary = {
  accuracy: document.getElementById("progressAccuracy"),
  difficulty: document.getElementById("progressDifficulty"),
  strongest: document.getElementById("progressStrongest"),
  weakest: document.getElementById("progressWeakest"),
  attempted: document.getElementById("progressAttempted"),
  correct: document.getElementById("progressCorrect"),
  questions: document.getElementById("progressQuestions"),
  streak: document.getElementById("progressStreak"),
};

const skillScoreList = document.getElementById("skillScoreList");
const recentActivityList = document.getElementById("recentActivityList");
const refreshButton = document.getElementById("refreshProgressPage");

async function fetchJson(url) {
  const response = await fetch(url);
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

function setText(element, value) {
  if (element) {
    element.textContent = value;
  }
}

function getSkillEntries(skills = {}) {
  return Object.entries(skills).map(([name, details]) => ({
    name,
    score: Math.max(0, Math.min(100, Number(details?.score ?? 0))),
    attempts: Number(details?.attempts ?? 0),
  }));
}

function getStrongestSkill(entries) {
  if (entries.length === 0) {
    return "Not available";
  }

  return formatSkillLabel(
    entries.reduce((best, current) => (
      current.score > best.score ? current : best
    )).name,
  );
}

function getWeakestSkill(entries) {
  if (entries.length === 0) {
    return "Not available";
  }

  return formatSkillLabel(
    entries.reduce((weakest, current) => (
      current.score < weakest.score ? current : weakest
    )).name,
  );
}

function renderSkillScores(entries) {
  skillScoreList.innerHTML = "";

  if (entries.length === 0) {
    const empty = document.createElement("div");
    empty.className = "status-card";
    empty.textContent = "No skill scores recorded yet.";
    skillScoreList.appendChild(empty);
    return;
  }

  entries
    .sort((left, right) => right.score - left.score)
    .forEach((skill) => {
      const row = document.createElement("article");
      row.className = "skill-score-row";

      const header = document.createElement("div");
      header.className = "skill-score-header";

      const name = document.createElement("strong");
      name.textContent = formatSkillLabel(skill.name);

      const meta = document.createElement("span");
      meta.textContent = `${skill.score}/100 | ${skill.attempts} attempts`;

      const track = document.createElement("div");
      track.className = "skill-bar-track";

      const bar = document.createElement("div");
      bar.className = "skill-bar-fill";
      bar.style.width = `${skill.score}%`;

      header.appendChild(name);
      header.appendChild(meta);
      track.appendChild(bar);
      row.appendChild(header);
      row.appendChild(track);
      skillScoreList.appendChild(row);
    });
}

function formatActivityTime(value) {
  if (!value) {
    return "Recently";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return "Recently";
  }

  return parsed.toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function renderRecentActivity(items = []) {
  recentActivityList.innerHTML = "";

  if (items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "status-card";
    empty.textContent = "No recent activity yet. Ask a question or complete practice to start tracking progress.";
    recentActivityList.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "activity-card";

    const question = document.createElement("strong");
    question.textContent = item.question || "Recorded activity";

    const meta = document.createElement("span");
    meta.textContent = [
      item.topic || "General",
      item.mode ? `Mode: ${item.mode}` : null,
      formatActivityTime(item.asked_at),
    ].filter(Boolean).join(" | ");

    card.appendChild(question);
    card.appendChild(meta);
    recentActivityList.appendChild(card);
  });
}

function renderProgress(state) {
  const stats = state.stats || {};
  const attempted = Number(stats.problems_attempted || 0);
  const correct = Number(stats.correct_answers || 0);
  const accuracy = attempted > 0
    ? Math.round((correct / attempted) * 10000) / 100
    : 0;
  const skillEntries = getSkillEntries(state.skill_progression || {});

  setText(summary.accuracy, `${accuracy}%`);
  setText(summary.difficulty, `Level ${state.difficulty_level ?? 1}`);
  setText(summary.strongest, getStrongestSkill(skillEntries));
  setText(summary.weakest, getWeakestSkill(skillEntries));
  setText(summary.attempted, String(attempted));
  setText(summary.correct, String(correct));
  setText(summary.questions, String(stats.questions_asked || 0));
  setText(summary.streak, String(state.correct_streak ?? 0));

  renderSkillScores(skillEntries);
  renderRecentActivity(state.recent_questions || []);
}

async function loadProgressPage() {
  refreshButton.disabled = true;
  try {
    const state = await fetchJson("/learning-state");
    renderProgress(state);
  } catch (error) {
    skillScoreList.innerHTML = "";
    recentActivityList.innerHTML = "";

    const skillError = document.createElement("div");
    skillError.className = "status-card";
    skillError.textContent = error.message || "Unable to load skill scores.";

    const activityError = document.createElement("div");
    activityError.className = "status-card";
    activityError.textContent = error.message || "Unable to load recent activity.";

    skillScoreList.appendChild(skillError);
    recentActivityList.appendChild(activityError);
  } finally {
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", loadProgressPage);

loadProgressPage();
