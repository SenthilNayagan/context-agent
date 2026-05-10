// -----------------------------------------------------
// ContextAgent UI logic
// -----------------------------------------------------

const API_URL = "http://127.0.0.1:8000/query";

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const newChatButton = document.getElementById("newChatButton");

const loadingEl = document.getElementById("loading");
const answerBox = document.getElementById("answerBox");
const answerText = document.getElementById("answerText");
const sourcesList = document.getElementById("sourcesList");
const elapsedTimeEl = document.getElementById("elapsedTime");
const errorBox = document.getElementById("errorBox");

// -----------------------------------------------------
// Helper functions
// -----------------------------------------------------

function showLoading() {
    loadingEl.classList.remove("hidden");
    answerBox.classList.add("hidden");
    errorBox.classList.add("hidden");
}

function hideLoading() {
    loadingEl.classList.add("hidden");
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
    answerBox.classList.add("hidden");
}

function showAnswer(answer, sources, elapsedSeconds) {
    // -------------------------------------------------
    // Render Markdown answer as safe HTML
    // -------------------------------------------------
    const html = marked.parse(answer);
    const safeHTML = DOMPurify.sanitize(html);
    answerText.innerHTML = safeHTML;

    // -------------------------------------------------
    // Render sources
    // -------------------------------------------------
    sourcesList.innerHTML = "";

    if (sources.length === 0) {
        const li = document.createElement("li");
        li.textContent = "No sources returned";
        sourcesList.appendChild(li);
    } else {
        sources.forEach(source => {
            const li = document.createElement("li");
            li.textContent = source;
            sourcesList.appendChild(li);
        });
    }

    elapsedTimeEl.textContent = `Elapsed time: ${elapsedSeconds}s`;

    answerBox.classList.remove("hidden");
    errorBox.classList.add("hidden");
}

// -----------------------------------------------------
// Ask button handler
// -----------------------------------------------------

askButton.addEventListener("click", async () => {
    const question = questionInput.value.trim();

    if (!question) {
        showError("Please enter a question.");
        return;
    }

    showLoading();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Request failed");
        }

        const data = await response.json();

        hideLoading();
        showAnswer(
            data.answer,
            data.sources || [],
            data.elapsed_seconds
        );

    } catch (err) {
        hideLoading();
        showError(`Error: ${err.message}`);
    }
});

// -----------------------------------------------------
// New Chat button handler
// -----------------------------------------------------

newChatButton.addEventListener("click", () => {
    // Clear input
    questionInput.value = "";

    // Clear answer & metadata
    answerText.innerHTML = "";
    sourcesList.innerHTML = "";
    elapsedTimeEl.textContent = "";

    // Hide UI elements
    answerBox.classList.add("hidden");
    loadingEl.classList.add("hidden");
    errorBox.classList.add("hidden");

    // Focus input for convenience
    questionInput.focus();
});