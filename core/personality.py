import random
from core.command_handler import get_task_counts

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the student eat his homework? Because the teacher told him it was a piece of cake!",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why was the math book sad? It had too many problems.",
    "What do you call a student who doesn't do homework? A mystery.",
]

GREETINGS = [
    "Hey! Ready to crush some tasks today?",
    "Welcome back! Let's make today productive.",
    "Hello! I've been waiting — let's get things done.",
    "Hi there! Your academic journey continues. What's the plan?",
    "Good to see you! Let's tackle that task list.",
]

FAREWELLS = [
    "Goodbye! You did great today. Rest well.",
    "See you next time! Keep that momentum going.",
    "Bye! Remember — small steps every day lead to big results.",
    "Take care! You're one step closer to your goals.",
    "Goodbye! Don't forget to rest — your brain needs it too.",
]

ENCOURAGEMENT_LOW = [
    "Hey, don't worry — every expert started somewhere. Let's pick one task and start!",
    "Looks like things are piling up. Want me to make a schedule?",
    "It's okay to fall behind. What matters is getting back up. Let's go!",
    "I believe in you! Try completing just one task today.",
]

ENCOURAGEMENT_MEDIUM = [
    "You're making solid progress! Keep it up.",
    "Not bad at all! A little more push and you'll be at the top.",
    "You're halfway there — stay consistent!",
    "Good work so far. Let's keep the momentum going.",
]

ENCOURAGEMENT_HIGH = [
    "You're absolutely crushing it! Outstanding work!",
    "Wow, look at that productivity! You're on fire!",
    "Top of the class energy right here. Keep going!",
    "Incredible! You're setting the bar high.",
]

SMALL_TALK = {
    "how are you": [
        "I'm just a bunch of code, but I'm feeling great knowing you're here!",
        "Running at full capacity and ready to help you succeed!",
        "Fantastic! Especially when I see you working hard.",
    ],
    "weather": [
        "I can't check the weather, but it's always a great day to study!",
        "Perfect study weather — whatever it is outside, it's cozy in here.",
    ],
    "joke": JOKES,
    "bored": [
        "Bored? Let's add a task and make something happen!",
        "Boredom is just productivity waiting to be unlocked. Want a challenge?",
    ],
    "thank": [
        "You're welcome! That's what I'm here for.",
        "Happy to help! You're doing great.",
        "Anytime! Keep up the amazing work.",
    ],
    "good morning": [
        "Good morning! Let's start the day strong. What's on your list?",
        "Morning! A new day, a fresh start. Let's make it count.",
    ],
    "good night": [
        "Good night! Rest well — your brain consolidates learning during sleep.",
        "Sweet dreams! You worked hard today.",
    ],
}

def get_mood_response():
    counts = get_task_counts()
    total = sum(counts.values())
    completed = counts.get("completed", 0)
    score = (completed / total * 100) if total > 0 else 0

    if score >= 70:
        return random.choice(ENCOURAGEMENT_HIGH)
    elif score >= 40:
        return random.choice(ENCOURAGEMENT_MEDIUM)
    else:
        return random.choice(ENCOURAGEMENT_LOW)

def get_greeting():
    return random.choice(GREETINGS)

def get_farewell():
    return random.choice(FAREWELLS)

def handle_small_talk(query):
    q = query.lower()
    for key, responses in SMALL_TALK.items():
        if key in q:
            return random.choice(responses)
    return None
