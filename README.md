# 🎓 Aria — AI Academic Assistant

An intelligent, voice-enabled academic assistant built with Python and Flask. Aria helps students manage tasks, predict grades using ML models, track productivity, collaborate in study groups, and stay motivated — all through a clean web interface or voice commands.

---

## 🚀 Features

### 📝 Task Management
- Add tasks with **priority** (high / medium / low), **category**, and **deadline**
- View, complete, and delete tasks with smart sorting
- Daily greeting with due-today reminders

### 📊 ML-Powered Academic Insights
- **Grade Prediction** — Linear Regression trained on 5,500+ student records (UCI + Exam Performance datasets)
- **Pass/Fail Prediction** — SVM classifier with RBF kernel
- **Student Profile Clustering** — K-Means (High Achiever / Average / At-Risk)
- **Study Recommendations** — data-driven advice based on real student averages
- **Dataset Visualization** — 9-panel insight graph (grade distribution, absences, test prep impact, etc.)

### 🏆 Gamification
- XP points for every action (add task = +5 XP, complete high priority = +30 XP)
- 7 level progression: Freshman → Sophomore → Junior → Senior → Graduate → Scholar → Academic Legend
- Streak tracking and badge system (First Step, On Fire, Deadline Crusher, Centurion, etc.)

### 🃏 Flashcards & Quiz
- Create, view, and delete flashcards
- Random quiz mode with answer checking and accuracy tracking

### 👥 Study Groups
- Create and join study groups
- Add and assign group tasks with priority
- Group productivity scoring and activity log

### 📅 Scheduler & Productivity
- Smart study schedule generator (deadline-aware, priority-sorted)
- Completion time predictor based on personal history
- 5-panel productivity dashboard graph (status, priority, category, trend)
- Overdue and upcoming deadline alerts

### 🎙️ Voice Support
- Voice input via microphone (speech-to-text)
- Text-to-speech responses
- Dual mode: voice or text input at startup

### 🌐 Web Interface
- Flask-based web app with user authentication (register / login)
- Real-time chat interface
- Sidebar with live XP status, task counts, and due-today list
- Image rendering for graphs directly in chat

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| ML Models | scikit-learn (LinearRegression, SVC, KMeans) |
| Data | pandas, NumPy |
| Visualization | Matplotlib |
| Database | SQLite |
| Voice | SpeechRecognition, pyttsx3 |
| Auth | Werkzeug (password hashing) |
| Deployment | Gunicorn, Vercel (wsgi) |

---

## 📁 Project Structure

```
ai_academic_assistant/
├── main.py                  # CLI entry point (voice/text mode)
├── wsgi.py                  # WSGI entry point for deployment
├── core/
│   ├── assistant_brain.py   # Central query router
│   ├── command_handler.py   # Task CRUD + XP rewards
│   ├── dataset_analysis.py  # ML models & dataset insights
│   ├── gamification.py      # XP, levels, streaks, badges
│   ├── flashcards.py        # Flashcard & quiz system
│   ├── groups.py            # Study group collaboration
│   ├── productivity.py      # Productivity analysis & graphs
│   ├── scheduler.py         # Deadlines, schedule, prediction
│   ├── personality.py       # Assistant personality responses
│   ├── quotes.py            # Motivational quotes
│   └── timer.py             # Pomodoro & countdown timer
├── web/
│   ├── app.py               # Flask routes & auth
│   ├── templates/           # HTML templates (index, login)
│   └── static/              # CSS & JavaScript
├── voice/
│   ├── speech_to_text.py    # Microphone input
│   └── text_to_speech.py    # Audio output
├── database/
│   └── db.py                # SQLite connection & init
├── data/
│   ├── combined_dataset.csv # Merged UCI + Exam dataset
│   ├── student-mat.csv      # UCI Math dataset
│   └── student-por.csv      # UCI Portuguese dataset
└── utils/
    └── config.py            # App config (name, DB path)
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-academic-assistant.git
cd ai-academic-assistant
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the web app
```bash
python web/app.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

### 5. Run in CLI mode (voice/text)
```bash
python main.py
```

---

## 💬 Command Reference

```
TASKS
  add task <name> [high/medium/low] [category <name>] [deadline YYYY-MM-DD]
  show tasks / show high tasks / show tasks category <name>
  complete task <number>
  delete task <number>

ML & DATASET
  recommend              - study advice from 5500+ student records
  grade predict          - predict grade (Linear Regression)
  my profile             - classify student type (K-Means)
  pass fail              - SVM pass/fail prediction
  exam insights          - exam performance analysis
  dataset insights       - full 9-panel visualization graph
  dataset summary        - dataset size and sources

FLASHCARDS
  create flashcard <question> | <answer>
  show flashcards
  quiz me
  delete flashcard <number>

STUDY GROUPS
  register <username>
  create group <name> as <username>
  join group <name> as <username>
  add group task <group> : <task> [assign <username>]
  show group tasks <name>
  group productivity <name>
  group members <name>
  group activity <name>
  list groups

PRODUCTIVITY
  productivity           - score and level
  show graph             - 5-panel dashboard
  deadlines              - overdue and upcoming
  schedule               - day-by-day study plan
  predict                - estimated completion time

OTHER
  timer <minutes>        - countdown timer
  pomodoro               - 25 min focus + 5 min break
  quote                  - motivational quote
  help                   - full command list
```

---

## 📊 Datasets Used

| Dataset | Source | Records | Use |
|---|---|---|---|
| UCI Student Performance (Math) | [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/Student+Performance) | ~395 | Grade prediction, clustering |
| UCI Student Performance (Portuguese) | UCI ML Repository | ~649 | Grade prediction, clustering |
| Exam Performance | Kaggle | ~1000 | Exam insights, test prep analysis |
| Synthetic (generated) | `data/generate_dataset.py` | ~3500 | Augmented training data |

---

## 🔐 Authentication

- Passwords are hashed using **Werkzeug's** `generate_password_hash` (PBKDF2-SHA256)
- Sessions are managed via Flask signed cookies
- Each user's tasks and data are isolated by `user_id`

---

## 🌍 Deployment

The app is configured for **Vercel** deployment via `vercel.json` and `wsgi.py`.  
On serverless environments, the SQLite database is stored in `/tmp` (auto-detected via `utils/config.py`).

---

## 📦 Requirements

```
flask
matplotlib
numpy
pandas
scikit-learn
colorama
gunicorn
```

---

## 🙌 Acknowledgements

- [UCI Machine Learning Repository](https://archive.ics.uci.edu/) — Student Performance dataset
- [Kaggle](https://www.kaggle.com/) — Exam Performance dataset
- [scikit-learn](https://scikit-learn.org/) — ML models
- [Flask](https://flask.palletsprojects.com/) — Web framework

---

> Built with ❤️ to make student life a little easier.
