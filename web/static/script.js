const messagesEl = document.getElementById("messages");
const inputEl    = document.getElementById("user-input");

function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  div.appendChild(bubble);
  messagesEl.appendChild(div);
  scrollBottom();
  return div;
}

function addTyping() {
  return addMessage("Aria is thinking...", "aria typing");
}

async function sendMessage() {
  const msg = inputEl.value.trim();
  if (!msg) return;

  addMessage(msg, "user");
  inputEl.value = "";

  const typing = addTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    typing.remove();

    if (data.type === "image") {
      const div = document.createElement("div");
      div.className = "message aria";
      const bubble = document.createElement("div");
      bubble.className = "bubble";
      const img = document.createElement("img");
      img.src = "data:image/png;base64," + data.image;
      img.style.cssText = "max-width:100%;border-radius:8px;margin-top:6px;";
      bubble.appendChild(img);
      div.appendChild(bubble);
      messagesEl.appendChild(div);
    } else {
      addMessage(data.response, "aria");
    }
    loadStatus();
  } catch (e) {
    typing.remove();
    addMessage("Something went wrong. Please try again.", "aria");
  }
}

function sendQuick(cmd) {
  inputEl.value = cmd;
  sendMessage();
}

async function loadStatus() {
  try {
    const res = await fetch("/status");
    const data = await res.json();
    document.getElementById("stat-pending").textContent   = data.pending;
    document.getElementById("stat-completed").textContent = data.completed;
    document.getElementById("xp-status").textContent      = data.xp_status;

    if (data.due_today.length > 0) {
      document.getElementById("due-today-section").style.display = "flex";
      document.getElementById("stat-due").textContent = data.due_today.length;
    }
  } catch (e) {}
}

// Send on Enter key
inputEl.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

// Load stats on startup
loadStatus();
