const API_BASE = "https://studytrack-improved.onrender.com";

const rosterList = document.querySelector("#roster-list");
const studentForm = document.querySelector("#student-form");
const errorBanner = document.querySelector("#error-banner");
const algorithmOutput = document.querySelector("#algorithm-output");

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
}

function clearError() {
  errorBanner.textContent = "";
  errorBanner.hidden = true;
}

async function request(path, options = {}) {
  clearError();

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });

    if (!response.ok) {
      let detail = `Request failed with status ${response.status}.`;
      try {
        const body = await response.json();
        if (body.detail) detail = body.detail;
      } catch (_) {}
      showError(detail);
      throw new Error(detail);
    }

    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    if (!errorBanner.textContent) {
      showError("Could not reach the StudyTrack backend.");
    }
    throw error;
  }
}

function createStudentCard(student) {
  const card = document.createElement("article");
  card.className = "student-card";
  card.dataset.id = student.id;

  const name = document.createElement("h3");
  name.textContent = student.name;

  const email = document.createElement("p");
  email.textContent = student.email;

  const ageText = document.createElement("p");
  ageText.className = "age-text";
  ageText.textContent = `Age: ${student.age}`;

  const ageInput = document.createElement("input");
  ageInput.type = "number";
  ageInput.min = "1";
  ageInput.value = student.age;
  ageInput.className = "age-input";

  const saveButton = document.createElement("button");
  saveButton.type = "button";
  saveButton.className = "save-age-button";
  saveButton.dataset.action = "save-age";
  saveButton.textContent = "Save Age";

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "delete-button";
  deleteButton.dataset.action = "delete";
  deleteButton.textContent = "Delete";

  card.append(name, email, ageText, ageInput, saveButton, deleteButton);
  return card;
}

function renderRoster(students) {
  rosterList.replaceChildren();

  for (const student of students) {
    rosterList.appendChild(createStudentCard(student));
  }
}

async function loadRoster() {
  const students = await request("/students/");
  renderRoster(students);
}

rosterList.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) return;

  const card = button.closest(".student-card");
  if (!card) return;

  const studentId = card.dataset.id;

  if (button.dataset.action === "save-age") {
    const input = card.querySelector(".age-input");
    const age = Number(input.value);

    if (!Number.isInteger(age) || age <= 0) {
      showError("Age must be a positive number.");
      return;
    }

    try {
      const updated = await request(`/students/${studentId}`, {
        method: "PATCH",
        body: JSON.stringify({ age })
      });
      card.querySelector(".age-text").textContent = `Age: ${updated.age}`;
    } catch (_) {}
  }

  if (button.dataset.action === "delete") {
    try {
      await request(`/students/${studentId}`, { method: "DELETE" });
      card.remove();
    } catch (_) {}
  }
});

studentForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(studentForm);
  const payload = {
    name: formData.get("name"),
    email: formData.get("email"),
    age: Number(formData.get("age"))
  };

  try {
    const student = await request("/students/", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    rosterList.appendChild(createStudentCard(student));
    studentForm.reset();
  } catch (_) {}
});

async function showSorted(field) {
  try {
    const students = await request(`/students/sorted?by=${field}`);
    algorithmOutput.textContent = students
      .map((s) => `${s.name} (${s.age})`)
      .join("\n");
  } catch (_) {}
}

document.querySelector("#sort-age").addEventListener("click", () => showSorted("age"));
document.querySelector("#sort-name").addEventListener("click", () => showSorted("name"));

document.querySelector("#search-button").addEventListener("click", async () => {
  const name = document.querySelector("#search-name").value.trim();
  if (!name) return showError("Enter an exact student name.");

  try {
    const student = await request(`/students/search?name=${encodeURIComponent(name)}`);
    algorithmOutput.textContent = JSON.stringify(student, null, 2);
  } catch (_) {}
});

document.querySelector("#report-button").addEventListener("click", async () => {
  const minAge = Number(document.querySelector("#min-age").value);

  try {
    const report = await request(`/students/report?min_age=${minAge}`);
    algorithmOutput.textContent =
      `${report.report}\n\nCount meeting minimum age: ${report.count_meeting_min_age}`;
  } catch (_) {}
});

document.querySelector("#summarize-button").addEventListener("click", async () => {
  const rawText = document.querySelector("#notes-input").value;

  try {
    const result = await request("/assistant/summarize", {
      method: "POST",
      body: JSON.stringify({ text: rawText })
    });
    document.querySelector("#summary-output").textContent =
      JSON.stringify(result, null, 2);
  } catch (_) {}
});

document.querySelector("#semantic-search-button").addEventListener("click", async () => {
  const query = document.querySelector("#semantic-query").value.trim();

  try {
    const result = await request(
      `/assistant/search?query=${encodeURIComponent(query)}&limit=5`
    );
    document.querySelector("#semantic-output").textContent =
      JSON.stringify(result, null, 2);
  } catch (_) {}
});

loadRoster().catch(() => {});
