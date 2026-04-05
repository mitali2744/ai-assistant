import re
from core.command_handler import add_task, show_tasks, complete_task, delete_task, get_due_today
from core.productivity import analyze_productivity, show_productivity_graph
from core.quotes import get_random_quote
from core.scheduler import check_deadlines, generate_study_schedule, predict_completion
from core.dataset_analysis import get_study_recommendation, predict_grade, cluster_student_profile, show_dataset_insights, get_exam_insights, get_dataset_summary, predict_pass_fail
from core.flashcards import add_flashcard, show_flashcards, start_quiz, check_answer, is_quiz_active, delete_flashcard
from core.groups import register_user, create_group, join_group, add_group_task, show_group_tasks, complete_group_task, group_productivity, list_groups, add_member, show_members, get_group_activity

# Timer callback will be injected from main.py
_speak_callback = None

def set_speak_callback(fn):
    global _speak_callback
    _speak_callback = fn

HELP_TEXT = """Available Commands:

TASKS
  add task <name> [high/medium/low] [category <name>] [deadline YYYY-MM-DD]
  show tasks
  show high tasks / show tasks category <name>
  complete task <number>
  delete task <number>

PRODUCTIVITY
  productivity       - check your score and level
  show graph         - visualize task dashboard
  deadlines          - see overdue and upcoming tasks
  schedule           - get a day-by-day study plan
  predict            - estimate time to finish pending tasks

ML & DATASET
  recommend          - study advice from 5500 student records
  grade predict      - predict your grade using Linear Regression
  my profile         - classify your student type using K-Means
  pass fail          - SVM pass/fail prediction
  exam insights      - analyze exam performance dataset
  dataset insights   - full dataset visualization graph
  dataset summary    - show dataset size and sources

FLASHCARDS
  create flashcard <question> | <answer>
  show flashcards
  quiz me            - start a random quiz
  delete flashcard <number>

STUDY GROUPS
  register <username>
  create group <name> as <username>
  join group <name> as <username>
  add group task <group> : <task> [assign <username>]
  show group tasks <name>
  complete group task <number>
  group productivity <name>
  group members <name>
  group activity <name>
  list groups

TIMER
  timer <minutes>    - start a countdown timer
  pomodoro           - 25 min focus + 5 min break

OTHER
  quote              - get a motivational quote
  recommend          - personalized study advice
  help               - show this list
  stop               - exit"""

def _extract_number(query):
    numbers = re.findall(r"\d+", query)
    return int(numbers[0]) if numbers else None

def _parse_add_task(query):
    """Extract task name, priority, category, deadline from query."""
    priority = "medium"
    category = "general"
    deadline = None

    # Extract priority
    p_match = re.search(r"\b(high|medium|low)\b", query)
    if p_match:
        priority = p_match.group(1)
        query = query[:p_match.start()] + query[p_match.end():]

    # Extract deadline
    d_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", query)
    if d_match:
        deadline = d_match.group(1)
        query = query[:d_match.start()] + query[d_match.end():]

    # Extract category
    c_match = re.search(r"category\s+(\w+)", query)
    if c_match:
        category = c_match.group(1)
        query = query[:c_match.start()] + query[c_match.end():]

    # Clean up task name
    task = re.sub(r".*add task\s*", "", query).strip()
    task = re.sub(r"\s+", " ", task).strip(".,!? ")

    return task, priority, category, deadline

def process_query(query, user_id=1):
    query = query.strip().strip(".,!?")
    q = query.lower().strip(".,!?")

    # ── Flashcards (must be checked early to avoid keyword conflicts) ──
    if "create flashcard" in q:
        parts = query.split("|")
        if len(parts) == 2:
            question = re.sub(r"(?i)create flashcard\s*", "", parts[0]).strip()
            answer = parts[1].strip()
            return add_flashcard(question, answer)
        return "Format: create flashcard <question> | <answer>"

    if "show flashcard" in q or "list flashcard" in q or q.strip() in ["cards", "flashcards", "show cards"]:
        return show_flashcards()

    if "delete flashcard" in q:
        num = _extract_number(q)
        if num:
            return delete_flashcard(num)
        return "Please specify flashcard number to delete."

    if "quiz me" in q or "start quiz" in q:
        return start_quiz()

    # If quiz is active, treat input as answer
    if is_quiz_active():
        return check_answer(query)

    # Greeting — check for name introduction first
    if "i'm" in q or "i am" in q or "my name is" in q:
        name_match = re.search(r"(?:i'm|i am|my name is)\s+(\w+)", q)
        if name_match and name_match.group(1) not in ["a", "the", "an", "your", "aria"]:
            return f"Nice to meet you, {name_match.group(1).capitalize()}! I am Aria. How can I help you today?"

    words = q.split()
    if len(words) <= 5 and any(w in words for w in ["hello", "hi", "hey"]):
        return "Hello! I am Aria, your academic assistant. How can I help you today?"

    if any(g in q for g in ["good morning", "good afternoon", "good evening", "good night"]):
        return "Good day! I am Aria, your academic assistant. How can I help you today?"

    if "thank" in q or "thanks" in q:
        return "You're welcome! Happy to help. Is there anything else you need?"

    if "add task" in q:
        task, priority, category, deadline = _parse_add_task(q)
        if not task:
            return "PROMPT_TASK"
        return add_task(task, priority, category, deadline, user_id=user_id)

    if "show tasks" in q or "list tasks" in q or "my tasks" in q:
        # Filter by priority: "show high tasks"
        p_match = re.search(r"\b(high|medium|low)\b", q)
        priority = p_match.group(1) if p_match else None
        # Filter by category: "show tasks category math"
        c_match = re.search(r"category\s+(\w+)", q)
        category = c_match.group(1) if c_match else None
        return show_tasks(category=category, priority=priority, user_id=user_id)

    if "complete task" in q or "mark task" in q or "finish task" in q:
        num = _extract_number(q)
        if num:
            return complete_task(num, user_id=user_id) + " " + get_random_quote()
        return "Please specify the task number to complete."

    if "delete task" in q or "remove task" in q:
        num = _extract_number(q)
        if num:
            return delete_task(num, user_id=user_id)
        return "Please specify the task number to delete."

    if "productivity" in q or "analyze" in q or "performance" in q:
        return analyze_productivity()

    if "show graph" in q or "graph" in q or "visualize" in q or "dashboard" in q:
        return show_productivity_graph()

    if "deadline" in q or "due" in q or "urgent" in q:
        return check_deadlines()

    if "schedule" in q or "study plan" in q or "plan" in q:
        return generate_study_schedule()

    if "predict" in q or "prediction" in q or "how long" in q:
        return predict_completion()

    if "timer" in q or "countdown" in q:
        from core.timer import start_timer
        num = _extract_number(q)
        if num and _speak_callback:
            return start_timer(num, _speak_callback)
        return "Please say 'timer 25' to start a 25 minute timer."

    if "pomodoro" in q:
        from core.timer import start_pomodoro
        if _speak_callback:
            return start_pomodoro(_speak_callback)
        return "Pomodoro could not start."

    if "quote" in q or "motivat" in q or "inspire" in q:
        return get_random_quote()

    if "recommend" in q or "study advice" in q or "study tip" in q:
        # Try to extract studytime hours from query e.g. "recommend 4 hours"
        num = _extract_number(q)
        hours = num if num else None
        return get_study_recommendation(studytime_hours_per_week=hours)

    if "grade predict" in q or "predict grade" in q or "predict my grade" in q or q.strip() in ["grades", "grade", "predict grade"]:
        # Extract numbers: studytime failures absences
        nums = re.findall(r"\d+", q)
        studytime = int(nums[0]) if len(nums) > 0 else 2
        failures  = int(nums[1]) if len(nums) > 1 else 0
        absences  = int(nums[2]) if len(nums) > 2 else 5
        return predict_grade(studytime, failures, absences)

    if "my profile" in q or "student profile" in q or "which student" in q:
        nums = re.findall(r"\d+", q)
        studytime = int(nums[0]) if len(nums) > 0 else 2
        failures  = int(nums[1]) if len(nums) > 1 else 0
        absences  = int(nums[2]) if len(nums) > 2 else 5
        goout     = int(nums[3]) if len(nums) > 3 else 3
        return cluster_student_profile(studytime, failures, absences, goout)

    if "pass fail" in q or "will i pass" in q or "pass or fail" in q or "svm" in q:
        nums = re.findall(r"\d+", q)
        studytime = int(nums[0]) if len(nums) > 0 else 2
        failures  = int(nums[1]) if len(nums) > 1 else 0
        absences  = int(nums[2]) if len(nums) > 2 else 5
        goout     = int(nums[3]) if len(nums) > 3 else 3
        health    = int(nums[4]) if len(nums) > 4 else 3
        return predict_pass_fail(studytime, failures, absences, goout, health)

    if "dataset" in q or "insights" in q or "dataset graph" in q:
        return show_dataset_insights()

    if "exam insight" in q or "exam analysis" in q or "exam performance" in q:
        return get_exam_insights()

    if "dataset summary" in q or "how many records" in q or "dataset size" in q:
        return get_dataset_summary()

    # ── Study Groups ──
    if q.startswith("register "):
        username = q.replace("register", "").strip()
        return register_user(username)

    if "create group" in q or "make group" in q or "new group" in q or "make a group" in q or "create a group" in q:
        # Skip filler words like "of", "a", "the", "my"
        m = re.search(r"(?:create|make|new)\s+(?:a\s+)?group\s+(?:of\s+\w+\s+)?(?:named?|called)?\s*(\w+)", q)
        if not m:
            m = re.search(r"(?:create|make|new)\s+(?:a\s+)?group\s+(\w+)(?!\s+(?:of|a|the|my))", q)
        user_m = re.search(r"\bas\s+(\w+)", q)
        if m and m.group(1) not in ["of", "a", "the", "my", "group", "named", "called", "two", "three", "four"]:
            return create_group(m.group(1), user_m.group(1) if user_m else "anonymous")
        return "Please give your group a name. Example: create group mathteam as mitali"

    if "join group" in q:
        m = re.search(r"join group\s+(\w+)", q)
        user_m = re.search(r"as\s+(\w+)", q)
        if m and user_m:
            return join_group(m.group(1), user_m.group(1))
        return "Format: join group <name> as <username>"

    if "add group task" in q:
        m = re.search(r"add group task\s+(\w+)\s*:\s*(.+?)(?:\s+assign\s+(\w+))?$", q)
        if m:
            priority_m = re.search(r"\b(high|medium|low)\b", q)
            priority = priority_m.group(1) if priority_m else "medium"
            return add_group_task(m.group(1), m.group(2).strip(), "user", m.group(3), priority)
        return "Format: add group task <group> : <task> [assign <username>]"

    if "show group tasks" in q:
        m = re.search(r"show group tasks\s+(\w+)", q)
        if m:
            return show_group_tasks(m.group(1))
        return "Format: show group tasks <group name>"

    if "complete group task" in q:
        num = _extract_number(q)
        if num:
            return complete_group_task(num)
        return "Please specify group task number."

    if "group productivity" in q:
        m = re.search(r"group productivity\s+(\w+)", q)
        if m:
            return group_productivity(m.group(1))
        return "Format: group productivity <group name>"

    if "list groups" in q or "show groups" in q:
        return list_groups()

    if "group members" in q or "show members" in q or "members of" in q or "members in" in q:
        m = re.search(r"(?:members of|members in|group members|show members)\s+(?:group\s+)?(\w+)", q)
        if m:
            return show_members(m.group(1))
        return "Format: group members <group name>"

    if "add member" in q:
        m = re.search(r"add member\s+(\w+)\s+(?:to\s+)?(\w+)", q)
        if m:
            return add_member(m.group(2), m.group(1))
        return "Format: add member <username> to <group name>"

    if "group activity" in q or "activity of" in q or "group log" in q:
        m = re.search(r"(?:group activity|activity of|group log)\s+(\w+)", q)
        if m:
            return get_group_activity(m.group(1))
        return "Format: group activity <group name>"

    if "help" in q or "what can you do" in q or "commands" in q:
        return HELP_TEXT

    if "your name" in q or "who are you" in q:
        return "I am AI assistant , your AI-based academic assistant built to help you manage tasks and track productivity."

    return "I didn't quite catch that. Try saying 'help' to see all commands, or rephrase your request."
