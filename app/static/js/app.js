const form = document.getElementById("analysis-form");
const results = document.getElementById("results");
const emptyState = document.getElementById("results-empty");
const errorBox = document.getElementById("error");

const similarityEl = document.getElementById("similarity");
const matchedCountEl = document.getElementById("matched-count");
const matchedSkillsEl = document.getElementById("matched-skills");
const missingSkillsEl = document.getElementById("missing-skills");
const roadmapEl = document.getElementById("roadmap");

const renderList = (container, items) => {
  container.innerHTML = "";
  if (!items.length) {
    const listItem = document.createElement("li");
    listItem.textContent = "None";
    container.appendChild(listItem);
    return;
  }
  items.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.textContent = item;
    container.appendChild(listItem);
  });
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.classList.add("hidden");

  const role = document.getElementById("role").value;
  const resume = document.getElementById("resume").value;

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ role, resume }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Unable to analyze resume.");
    }

    similarityEl.textContent = `${payload.similarity}%`;
    matchedCountEl.textContent = `${payload.matched_skills.length}`;

    renderList(matchedSkillsEl, payload.matched_skills);
    renderList(missingSkillsEl, payload.missing_skills);
    renderList(roadmapEl, payload.roadmap);

    emptyState.classList.add("hidden");
    results.classList.remove("hidden");
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.classList.remove("hidden");
  }
});
