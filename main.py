from voice.speech_to_text import listen
from voice.text_to_speech import speak
from core.assistant_brain import process_query

def run_assistant():
    speak("Hello Mitali, your AI academic assistant is ready")

    while True:
        query = listen()

        if query:
            print("You said:", query)

            if "stop" in query.lower():
                speak("Goodbye Mitali")
                break

            response = process_query(query)
            speak(response)

run_assistant()