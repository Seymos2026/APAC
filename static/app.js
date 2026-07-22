const form = document.getElementById("classify-form");
const toggleManualBtn = document.getElementById("toggle-manual");
const manualBlock = document.getElementById("manual-block");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const submitBtn = document.getElementById("submit-btn");

toggleManualBtn.addEventListener("click", () => {
  manualBlock.classList.toggle("hidden");
  toggleManualBtn.textContent = manualBlock.classList.contains("hidden")
    ? "Paste abstract manually instead"
    : "Hide manual abstract field";
});

function setStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.className = kind || "";
  statusEl.classList.toggle("hidden", !message);
}

function renderResult(data) {
  resultEl.classList.remove("hidden");

  document.getElementById("result-title").textContent = data.title || "Classification result";
  document.getElementById("result-doi").textContent = data.doi ? `DOI: ${data.doi}` : "";

  document.getElementById("predicted-label").textContent = data.label;
  document.getElementById("predicted-confidence").textContent =
    `${(data.confidence * 100).toFixed(1)}% confidence`;

  const barsEl = document.getElementById("prob-bars");
  barsEl.innerHTML = "";
  data.probabilities.forEach((p) => {
    const pct = (p.probability * 100).toFixed(1);
    const row = document.createElement("div");
    row.className = "prob-row";
    row.innerHTML = `
      <span>${p.label}</span>
      <span class="prob-track"><span class="prob-fill" style="width:${pct}%"></span></span>
      <span>${pct}%</span>
    `;
    barsEl.appendChild(row);
  });

  const kwEl = document.getElementById("keywords");
  kwEl.innerHTML = "";
  (data.keywords || []).forEach((kw) => {
    const chip = document.createElement("span");
    chip.className = "keyword-chip";
    chip.textContent = kw;
    kwEl.appendChild(chip);
  });

  document.getElementById("abstract-used").textContent = data.abstract;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  resultEl.classList.add("hidden");
  setStatus("Classifying...", "loading");
  submitBtn.disabled = true;

  const doi = document.getElementById("doi").value.trim();
  const abstract = document.getElementById("abstract").value.trim();

  try {
    const resp = await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ doi, abstract }),
    });
    const data = await resp.json();

    if (!resp.ok) {
      setStatus(data.error || "Something went wrong.", "error");
      return;
    }

    setStatus("", "");
    renderResult(data);
  } catch (err) {
    setStatus(`Request failed: ${err.message}`, "error");
  } finally {
    submitBtn.disabled = false;
  }
});
