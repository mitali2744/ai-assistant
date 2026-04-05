import random
from database.db import get_connection

def init_flashcards(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            correct INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def add_flashcard(question, answer):
    question, answer = question.strip(), answer.strip()
    if not question or not answer:
        return "Please provide both a question and answer."
    conn = get_connection()
    init_flashcards(conn)
    conn.execute("INSERT INTO flashcards (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()
    return f"Flashcard saved! Q: '{question}'"

def show_flashcards():
    conn = get_connection()
    init_flashcards(conn)
    rows = conn.execute("SELECT id, question, answer, correct, attempts FROM flashcards").fetchall()
    conn.close()
    if not rows:
        return "No flashcards yet. Create one with: create flashcard <question> | <answer>"
    lines = ["Your Flashcards", "-" * 40]
    for r in rows:
        acc = str(r[3]) + "/" + str(r[4]) if r[4] > 0 else "untested"
        lines.append(str(r[0]) + ". Q: " + r[1])
        lines.append("   A: " + r[2] + "  [" + acc + "]")
    return "\n".join(lines)

def delete_flashcard(card_id):
    conn = get_connection()
    init_flashcards(conn)
    conn.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()
    return f"Flashcard {card_id} deleted."

# In-memory quiz state
_quiz_state = {"active": False, "card_id": None, "question": None, "answer": None}

def start_quiz():
    conn = get_connection()
    init_flashcards(conn)
    rows = conn.execute("SELECT id, question, answer FROM flashcards").fetchall()
    conn.close()
    if not rows:
        return "No flashcards to quiz on. Add some first!"
    card = random.choice(rows)
    _quiz_state.update({"active": True, "card_id": card[0], "question": card[1], "answer": card[2]})
    return f"QUIZ: {card[1]}\n(Type your answer or 'skip' to skip)"

def check_answer(user_answer):
    if not _quiz_state["active"]:
        return "No active quiz. Type 'quiz me' to start."
    correct_answer = _quiz_state["answer"].lower().strip()
    user_answer = user_answer.lower().strip()
    card_id = _quiz_state["card_id"]

    conn = get_connection()
    is_correct = correct_answer in user_answer or user_answer in correct_answer
    conn.execute(
        "UPDATE flashcards SET attempts=attempts+1, correct=correct+? WHERE id=?",
        (1 if is_correct else 0, card_id)
    )
    conn.commit()
    conn.close()
    _quiz_state["active"] = False

    if is_correct:
        return f"Correct! The answer was: {_quiz_state['answer']}. Type 'quiz me' for another."
    else:
        return f"Not quite. The correct answer was: {_quiz_state['answer']}. Keep studying!"

def is_quiz_active():
    return _quiz_state["active"]
