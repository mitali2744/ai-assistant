const messagesEl  = document.getElementById("messages");
const inputEl     = document.getElementById("user-input");
const micBtn      = document.getElementById("mic-btn");
const voiceStatus = document.getElementById("voice-status");

let isListening = false;
let recognition = null;

if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = "en-US";

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add("active");
    voiceStatus.textContent = "🔴 Listening...";
    voiceStatus.classList.add("listening");
    inputEl.placeholder = "Listening... seak now";
  };

  recognition.onresult = (e) => {
    let transcript = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      transcript += e.results[i][0].transcript;
    }
    inputEl.value = transcript;
    if (e.results[e.results.length - 1].isFinal) {
      stopListening();
      sendMessage();
    }
  };

  recognition.onerror = () => stopListening();
  recognition.onend   = () => stopListening();
} else {
  micBtn.title = "Voice not supported. Use Chrome.";
  micBtn.style.opacity = "0.3";
}

function toggleVoice() {
  if (!recognition) { addMessage("Voice not supported. Please use Chrome.", "aria"); return; }
  isListening ? recognitart();
}

function stopListening() {
  isListening = false;
  micBtn.classList.remove("active");
  voiceStatus.textContent = "🎤 Voice Ready";
  voiceStatus.classList.remove("listening");
  inputEl.placeholder = "Type a message or click 🎤 to speak...";
}

function ariaSpeak(text) {
  if (!window.speechSynthesis || !text || text.length > 300) return;
  window.speechSynthesis.cancel();
    if (data.type === "image") {
      const div = document.createElement("div"); div.className = "message aria";
      const av = document.createElement("div"); av.className = "avatar-sm"; av.textContent = "A";
      const bubble = document.createElement("div"); bubble.className = "bubble";
      const img = document.createElement("img"); img.src = "data:image/png;base64," + data.image; img.style.cssText = "max-width:100%;border-radius:10px;margin-top:6px;";
      bubble.appendChild(img); div.appendChild(av); div.appendChild(bubble); messagesEl.appendChild(div); scrollBottom();
    } else if (data.type === "table") {
      const div = document.createElement("div"); div.className = "message aria";
      const av = document.createElement("div"); av.className = "avatar-sm"; av.textContent = "A";
      const bubble = document.createElement("div"); bubble.className = "bubble";
      bubble.innerHTML = data.html;
      div.appendChild(av); div.appendChild(bubble); messagesEl.appendChild(div); scrollBottom();
    } else { addMessage(data.response, "aria"); ariaSpeak(data.response); }

function scrollBottom() { messagesEl.scrollTop = messagesEl.scrollHeight; }

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  if (sender === "aria") {
    const av = document.createElement("div");
    av.className = "avatar-sm";
    av.textContent = "A";
    div.appendChild(av);
  }
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  div.appendChild(bubble);
  messagesEl.appendChild(div);
  scrollBottom();
  return div;
}

function addTyping() {
  const div = document.createElement("div");
  div.className = "message aria typing";
  const av = document.createElement("div");
  av.className = "avatar-sm"; av.textContent = "A";
  const bubble = do"div");
  bubble.className = "bubble"; bubble.textContent = "Aria is thinking...";
  div.appendChild(av); div.appendChild(bubble);
  messagesEl.appendChild(div);
  scrollBottom();
  return div;
}

async function sendMessage() {
  const msg = inputEl.value.trim();
  if (!msg) return;
  addMessage(msg, "user");
  inputEl.value = "";
  const typing = addTyping();

  try {
    const res  = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    typing.remove();

 = "image") {
      const div = document.createElement("div");
      div.className = "message aria";
      const av = document.createElement("div");
      av.className = "avatar-sm"; av.textContent = "A";
      const bubble = document.createElement("div");
      bubble.className = "bubble";
      const img = document.createElement("img");
      img.src = "data:image/png;base64," + data.image;
      img.style.cssText = "max-width:100%;border-radius:10px;margin-top:6px;";
      bubble.appendChild(img);
      div.appendChild(av); div.appendChild(bubble);
      messagesEl.appendChild(div);
      scrollBottom();
    } else {
      addMessage(data.response, "aria");
      ariaSpeak(data.response);
    }
    loadStatus();
  } catch {
    typing.remove();
    addMessage("Something went wrong. Please try again.", "aria");
  }
}

function sendQuick(cmd) { inputEl.value = cmd; sendMessage(); }

async function loadStatus() {
  try {
    const res  = await fetch("/status");
    const data = await res.json();
    document.getElementById("stat-pending").textContent   = data.pending;
    document.getElementById("stat-completed").textContent = data.completed;
    document.getElementById("xp-st      = data.xp_status;

    const xpMatch = data.xp_status.match(/(\d+)\s*XP\s*\/\s*(\d+)/);
    if (xpMatch) {
      const pct = Math.min((parseInt(xpMatch[1]) / parseInt(xpMatch[2])) * 100, 100);
      document.getElementById("xp-bar").style.width = pct + "%";
    }
    const lvlMatch = data.xp_status.match(/Level:\s*([^|]+)/);
    if (lvlMatch) document.getElementById("xp-level").textContent = lvlMatch[1].trim();

    if (data.due_today.length > 0) {
      document.getEl "flex";
      document.getElementById("stat-due").textContent = data.due_today.length;
    }
  } catch {}
}

inputEl.addEventListener("keydown", e => { if (e.key === "Enter") sendMessage(); });
window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
loadStatus();
