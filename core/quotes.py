import random

QUOTES = [
    "The secret of getting ahead is getting started. — Mark Twain",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "Success is the sum of small efforts repeated day in and day out. — Robert Collier",
    "Believe you can and you're halfway there. — Theodore Roosevelt",
    "You don't have to be great to start, but you have to start to be great. — Zig Ziglar",
    "Hard work beats talent when talent doesn't work hard. — Tim Notke",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Stay focused and never give up.",
    "Every expert was once a beginner.",
]

def get_random_quote():
    return random.choice(QUOTES)
