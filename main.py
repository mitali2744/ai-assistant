from database.db import init_db
from voice.text_to_speech import speak
from core.assistant_brain import process_query, set_speak_callback
from core.command_handler import get_due_today, get_task_counts
from utils.config import ASSISTANT_NAME

def get_input_voice():
    from voice.speech_to_text import listen
    return listen()

def get_input_text():
    try:
        return input("You: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "stop"

def daily_greeting():
    counts = get_task_counts()
    pending = counts.get("pending", 0)
    completed = counts.get("completed", 0)
    due_today = get_due_today()

    greeting = f"Good day! I am {ASSISTANT_NAME}, your academic assistant. "
    if pending == 0:
        greeting += "You have no pending tasks. "
    else:
        greeting += f"You have {pending} pending task(s) and {completed} completed. "
    if due_today:
        names = ", ".join([t[1] for t in due_today])
        greeting += f"Tasks due today: {names}. "
    greeting += "Type 'help' to see all commands."
    return greeting

def run_assistant():
    init_db()
    set_speak_callback(speak)

    print("\n--- AI Assistant: AI Academic Assistant ---")
    print("Choose input mode:")
    print("  1. Voice")
    print("  2. Text")
    choice = input("Enter 1 or 2: ").strip()
    use_voice = choice == "1"

    speak(daily_greeting())

    while True:
        if use_voice:
            query = get_input_voice()
            if query is None:
                speak("I didn't catch that. Please try again.")
                continue
        else:
            query = get_input_text()

        if not query:
            continue

        print(f"You: {query}")

        if any(w in query.lower() for w in ["stop", "exit", "quit", "bye"]):
            speak("Goodbye! Keep up the great work.")
            break

        response = process_query(query)

        if response == "PROMPT_TASK":
            speak("What task would you like to add?")
            task_input = get_input_voice() if use_voice else get_input_text()
            if task_input:
                print(f"You: {task_input}")
                speak("Priority? Say high, medium, or low. Or press Enter to skip.")
                pri_input = get_input_voice() if use_voice else get_input_text()
                priority = pri_input.strip().lower() if pri_input in ["high", "medium", "low"] else "medium"
                speak("Category? E.g. math, AI, physics. Or press Enter to skip.")
                cat_input = get_input_voice() if use_voice else get_input_text()
                category = cat_input.strip() if cat_input else "general"
                speak("Deadline? Enter date as YYYY-MM-DD or press Enter to skip.")
                dl_input = get_input_voice() if use_voice else get_input_text()
                import re
                dl_match = re.search(r"\d{4}-\d{2}-\d{2}", dl_input) if dl_input else None
                deadline = dl_match.group(0) if dl_match else None
                response = process_query(f"add task {task_input} {priority} category {category} {deadline or ''}")
            else:
                response = "No task provided."

        speak(response)

if __name__ == "__main__":
    run_assistant()
