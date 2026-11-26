
// ---------- Theme toggle ----------
const root = document.documentElement;
const themeToggle = document.getElementById("themeToggle");

function applyTheme(theme) {
  const isLight = theme === "light";
  root.dataset.theme = isLight ? "light" : "dark";

  if (themeToggle) {
    themeToggle.querySelector(".theme-icon").textContent = isLight ? "☾" : "☼";
    themeToggle.querySelector(".theme-label").textContent = isLight ? "Dark" : "Light";
    themeToggle.setAttribute(
      "aria-label",
      isLight ? "Switch to dark theme" : "Switch to light theme"
    );
    themeToggle.setAttribute(
      "title",
      isLight ? "Switch to dark theme" : "Switch to light theme"
    );
  }
}

try {
  const savedTheme = localStorage.getItem("healthcare-theme");
  applyTheme(savedTheme === "light" ? "light" : "dark");
} catch (e) {
  applyTheme("dark");
}

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    try {
      localStorage.setItem("healthcare-theme", nextTheme);
    } catch (e) {}
  });
}

// ---------- Navbar scroll effect ----------
const navbar = document.getElementById("navbar");
if (navbar) {
  const onScroll = () => navbar.classList.toggle("scrolled", window.scrollY > 12);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

// ---------- Scroll reveal ----------
const revealTargets = document.querySelectorAll(
  ".card, .pill, .hero-visual, .stat-strip .card"
);
revealTargets.forEach((el, i) => {
  el.classList.add("reveal");
  el.style.transitionDelay = `${Math.min(i % 6, 5) * 70}ms`;
});

if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  revealTargets.forEach((el) => io.observe(el));
} else {
  revealTargets.forEach((el) => el.classList.add("visible"));
}

// ---------- Animated stat donuts ----------
document.querySelectorAll(".donut[data-pct]").forEach((donut) => {
  const target = parseFloat(donut.dataset.pct) || 0;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      donut.style.setProperty("--pct", target);
    });
  });
});

// ---------- Mobile nav ----------
const navToggle = document.getElementById("navToggle");
const navLinks = document.getElementById("navLinks");
if (navToggle) {
  navToggle.addEventListener("click", () => {
    const isOpen = navLinks.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });
  navLinks.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => navLinks.classList.remove("open"));
  });
}

// ---------- Tabs ----------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`panel-${btn.dataset.tab}`).classList.add("active");
  });
});

if (window.location.hash === "#heart") {
  const heartTab = document.querySelector('.tab-btn[data-tab="heart"]');
  if (heartTab) heartTab.click();
}

// ---------- Symptom picker ----------
const symptomGrid = document.getElementById("symptomGrid");
const symptomSearch = document.getElementById("symptomSearch");
const selectedCountEl = document.getElementById("selectedCount");
const predictSymptomsBtn = document.getElementById("predictSymptomsBtn");
const symptomResult = document.getElementById("symptomResult");

function updateSelectedCount() {
  if (!symptomGrid) return;
  const count = symptomGrid.querySelectorAll("input:checked").length;
  selectedCountEl.textContent = count;
}

if (symptomGrid) {
  symptomGrid.addEventListener("change", (e) => {
    if (e.target.matches("input[type=checkbox]")) {
      e.target.closest(".symptom-chip").classList.toggle("selected", e.target.checked);
      updateSelectedCount();
    }
  });
}

if (symptomSearch) {
  symptomSearch.addEventListener("input", () => {
    const q = symptomSearch.value.trim().toLowerCase();
    symptomGrid.querySelectorAll(".symptom-chip").forEach((chip) => {
      const match = chip.dataset.label.includes(q);
      chip.style.display = match ? "flex" : "none";
    });
  });
}

function urgencyBadgeClass(urgency) {
  if (urgency === "emergency") return "badge-emergency";
  if (urgency === "self-care") return "badge-self-care";
  return "badge-see-doctor";
}

function urgencyLabel(urgency) {
  if (urgency === "emergency") return "Emergency";
  if (urgency === "self-care") return "Self-care";
  return "See a doctor";
}

if (predictSymptomsBtn) {
  predictSymptomsBtn.addEventListener("click", async () => {
    const selected = Array.from(symptomGrid.querySelectorAll("input:checked")).map((i) => i.value);
    if (selected.length === 0) {
      symptomResult.classList.add("show");
      symptomResult.innerHTML = `<p style="color: var(--warning); margin:0;">Please select at least one symptom first.</p>`;
      return;
    }

    predictSymptomsBtn.disabled = true;
    predictSymptomsBtn.textContent = "Analyzing...";

    try {
      const res = await fetch("/predict-symptoms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms: selected }),
      });
      const data = await res.json();

      if (!res.ok) {
        symptomResult.innerHTML = `<p style="color: var(--warning); margin:0;">${data.error}</p>`;
      } else {
        symptomResult.innerHTML = `
          <span class="badge ${urgencyBadgeClass(data.urgency)}">${urgencyLabel(data.urgency)}</span>
          <h3 style="margin-top:14px;">${data.disease}</h3>
          <p>${data.description}</p>
          <p><strong>Guidance:</strong> ${data.advice}</p>
          ${data.confidence !== null ? `<p style="font-size:0.8rem;">Model confidence: ${data.confidence}%</p>` : ""}
        `;
      }
      symptomResult.classList.add("show");
    } catch (err) {
      symptomResult.classList.add("show");
      symptomResult.innerHTML = `<p style="color: var(--danger); margin:0;">Something went wrong. Please try again.</p>`;
    } finally {
      predictSymptomsBtn.disabled = false;
      predictSymptomsBtn.textContent = "Predict Disease";
    }
  });
}

// ---------- Heart form ----------
const heartForm = document.getElementById("heartForm");
const heartResult = document.getElementById("heartResult");
const HEART_FIELDS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
  "thalach", "exang", "oldpeak", "slope", "ca", "thal"];

if (heartForm) {
  heartForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {};
    HEART_FIELDS.forEach((f) => {
      payload[f] = document.getElementById(f).value;
    });

    const submitBtn = heartForm.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Assessing...";

    try {
      const res = await fetch("/predict-heart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (!res.ok) {
        heartResult.innerHTML = `<p style="color: var(--warning); margin:0;">${data.error}</p>`;
      } else {
        const badgeClass = data.at_risk ? "badge-emergency" : "badge-self-care";
        const badgeText = data.at_risk ? "Elevated Risk" : "Low Risk";
        heartResult.innerHTML = `
          <span class="badge ${badgeClass}">${badgeText}</span>
          <h3 style="margin-top:14px;">Estimated risk probability: ${data.risk_probability}%</h3>
          <p>${data.message}</p>
        `;
      }
      heartResult.classList.add("show");
    } catch (err) {
      heartResult.classList.add("show");
      heartResult.innerHTML = `<p style="color: var(--danger); margin:0;">Something went wrong. Please try again.</p>`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Assess Heart Disease Risk";
    }
  });
}

// ---------- Chatbot widget ----------
const chatToggle = document.getElementById("chatToggle");
const chatWindow = document.getElementById("chatWindow");
const chatClose = document.getElementById("chatClose");
const chatBody = document.getElementById("chatBody");
const chatInput = document.getElementById("chatInput");
const chatSend = document.getElementById("chatSend");

function appendMessage(text, sender) {
  const msg = document.createElement("div");
  msg.className = `chat-msg ${sender}`;
  msg.textContent = text;
  chatBody.appendChild(msg);
  chatBody.scrollTop = chatBody.scrollHeight;
}

async function sendChat() {
  const text = chatInput.value.trim();
  if (!text) return;
  appendMessage(text, "user");
  chatInput.value = "";

  try {
    const res = await fetch("/assistant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text }),
    });
    const data = await res.json();
    appendMessage(res.ok ? data.reply : data.error, "bot");
  } catch (err) {
    appendMessage("Sorry, I couldn't reach the assistant right now.", "bot");
  }
}

if (chatToggle) {
  chatToggle.addEventListener("click", () => chatWindow.classList.toggle("open"));
  chatClose.addEventListener("click", () => chatWindow.classList.remove("open"));
  chatSend.addEventListener("click", sendChat);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendChat();
  });
}
