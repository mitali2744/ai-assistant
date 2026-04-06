// DOM element references
const messagesEl  = document.getElementById("messages");
const inputEl     = document.getElementById("user-input");
const micBtn      = document.getElementById("mic-btn");
const voiceStatus = document.getElementById("voice-status");

let isListening = false;  // is mic currently active?
let recognition = null;   // SpeechRecognition instance

// set up voice recognition if browser supports it (Chrome/Edge)
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.continuous     = false;   // stop after one utterance
  recognition.interimResults = true;    // show partial text while speaking
  recognition.lang           = "en-US";

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add("active");
    voiceStatus.textContent = "🔴 Listening...";
    voiceStatus.classList.add("listening");
    inputEl.placeholder = "Listening... speak now";
  };

  recognition.onresult = (e) => {
    let transcript = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      transcript += e.results[i][0].transcript;  // build full transcript
    }
    inputEl.value = transcript;  // show in input box
    if (e.results[e.results.length - 1].isFinal) {
      stopListening();
      sendMessage();  // auto-send when speech ends
    }
  };

  recognition.onerror = () => stopListening();
  recognition.onend   = () => stopListening();
} else {
  if (micBtn) {
    micBtn.title = "Voice not supported. Use Chrome.";
    micBtn.style.opacity = "0.3";
  }
}

function toggleVoice() {
  if (!recognition) { addMessage("Voice not supported. Please use Chrome.", "aria"); return; }
  if (isListening) {
    recognition.stop();   // stop if already listening
  } else {
    recognition.start();  // start listening
  }
}

function stopListening() {
  // reset mic UI back to idle state
  isListening = false;
  if (micBtn) micBtn.classList.remove("active");
  if (voiceStatus) {
    voiceStatus.textContent = "🎤 Voice Ready";
    voiceStatus.classList.remove("listening");
  }
  inputEl.placeholder = "Type a message or click 🎤 to speak...";
}

function ariaSpeak(text) {
  // read Aria's response aloud using browser TTS
  if (!window.speechSynthesis || !text || text.length > 300) return;
  window.speechSynthesis.cancel();  // stop any current speech
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1; utter.pitch = 1;
  window.speechSynthesis.speak(utter);
}

function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;  // scroll to latest message
}

function addMessage(text, sender) {
  // create and append a chat bubble to the messages area
  const div = document.createElement("div");
  div.className = `message ${sender}`;  // "message aria" or "message user"
  if (sender === "aria") {
    const av = document.createElement("div");
    av.className = "avatar-sm";
    av.textContent = "A";  // Aria's avatar
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
  // show "Aria is thinking..." while waiting for server response
  const div    = document.createElement("div"); div.className = "message aria typing";
  const av     = document.createElement("div"); av.className = "avatar-sm"; av.textContent = "A";
  const bubble = document.createElement("div"); bubble.className = "bubble"; bubble.textContent = "Aria is thinking...";
  div.appendChild(av); div.appendChild(bubble);
  messagesEl.appendChild(div);
  scrollBottom();
  return div;
}

async function sendMessage() {
  const msg = inputEl.value.trim();
  if (!msg) return;              // do nothing if input is empty
  addMessage(msg, "user");       // show user's message in chat
  inputEl.value = "";            // clear input box
  const typing = addTyping();    // show typing indicator

  try {
    // send message to Flask /chat endpoint as JSON
    const res  = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });
    const data = await res.json();
    typing.remove();  // remove typing indicator

    if (data.type === "image") {
      // render base64 image response
      const div    = document.createElement("div"); div.className = "message aria";
      const av     = document.createElement("div"); av.className = "avatar-sm"; av.textContent = "A";
      const bubble = document.createElement("div"); bubble.className = "bubble";
      const img    = document.createElement("img");
      img.src = "data:image/png;base64," + data.image;
      img.style.cssText = "max-width:100%;border-radius:10px;margin-top:6px;";
      bubble.appendChild(img); div.appendChild(av); div.appendChild(bubble);
      messagesEl.appendChild(div); scrollBottom();
    } else if (data.type === "table") {
      // render HTML table response
      const div    = document.createElement("div"); div.className = "message aria";
      const av     = document.createElement("div"); av.className = "avatar-sm"; av.textContent = "A";
      const bubble = document.createElement("div"); bubble.className = "bubble";
      bubble.innerHTML = data.html;
      div.appendChild(av); div.appendChild(bubble);
      messagesEl.appendChild(div); scrollBottom();
    } else {
      addMessage(data.response, "aria");  // show text response
      ariaSpeak(data.response);           // read it aloud
    }
    loadStatus();  // refresh sidebar stats after each message
  } catch {
    typing.remove();
    addMessage("Something went wrong. Please try again.", "aria");
  }
}

function sendQuick(cmd) {
  // called by quick action buttons — fills input and sends
  inputEl.value = cmd;
  sendMessage();
}

async function loadStatus() {
  // fetch and update sidebar: pending/completed counts, XP bar, due today
  try {
    const res  = await fetch("/status");
    const data = await res.json();
    document.getElementById("stat-pending").textContent   = data.pending;
    document.getElementById("stat-completed").textContent = data.completed;

    if (data.xp_status) {
      document.getElementById("xp-status").textContent = data.xp_status;

      // parse XP numbers from status string e.g. "50 XP / 100 XP"
      const xpMatch = data.xp_status.match(/(\d+)\s*XP\s*\/\s*(\d+)/);
      if (xpMatch) {
        const pct = Math.min((parseInt(xpMatch[1]) / parseInt(xpMatch[2])) * 100, 100);
        document.getElementById("xp-bar").style.width = pct + "%";  // update progress bar
      }
      // parse level name from status string e.g. "Level: Junior"
      const lvlMatch = data.xp_status.match(/Level:\s*([^|]+)/);
      if (lvlMatch) document.getElementById("xp-level").textContent = lvlMatch[1].trim();
    }

    if (data.due_today && data.due_today.length > 0) {
      document.getElementById("due-box").style.display = "flex";  // show due today box
      document.getElementById("stat-due").textContent = data.due_today.length;
    }
  } catch {}
}

// send message when user presses Enter key
inputEl.addEventListener("keydown", e => { if (e.key === "Enter") sendMessage(); });

// preload voices for TTS
if (window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

loadStatus();  // load sidebar stats on page load
